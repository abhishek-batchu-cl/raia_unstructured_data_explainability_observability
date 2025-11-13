"""
PII/PHI Redactor with pluggable rulesets for deterministic scrubbing.
"""

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Callable


@dataclass
class RedactionRule:
    """A single redaction rule."""

    rule_id: str
    pattern: str  # Regex pattern
    replacement: str = "[REDACTED]"
    fields: List[str] = None  # Specific fields to apply to (None = all strings)
    hash_match: bool = False  # If True, replace with hash instead of generic string

    def __post_init__(self):
        self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE)


# Pre-defined rulesets for common PII/PHI patterns
DEFAULT_PII_RULES = [
    # Email addresses
    RedactionRule(
        rule_id="pii_email",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        replacement="[EMAIL_REDACTED]",
    ),
    # US Phone numbers
    RedactionRule(
        rule_id="pii_phone_us",
        pattern=r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
        replacement="[PHONE_REDACTED]",
    ),
    # US SSN
    RedactionRule(
        rule_id="pii_ssn",
        pattern=r"\b\d{3}-\d{2}-\d{4}\b",
        replacement="[SSN_REDACTED]",
    ),
    # Credit card numbers (simple pattern)
    RedactionRule(
        rule_id="pii_credit_card",
        pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        replacement="[CC_REDACTED]",
    ),
    # IP addresses
    RedactionRule(
        rule_id="pii_ip_address",
        pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        replacement="[IP_REDACTED]",
    ),
]

PHI_RULES = [
    # Medical record numbers (MRN) - simplified pattern
    RedactionRule(
        rule_id="phi_mrn",
        pattern=r"\b(?:MRN|mrn|medical record)[\s:]*([A-Z0-9]{6,})\b",
        replacement="[MRN_REDACTED]",
    ),
    # Patient ID patterns
    RedactionRule(
        rule_id="phi_patient_id",
        pattern=r"\b(?:patient[_\s]?id|pat[_\s]?id)[\s:]*([A-Z0-9]{6,})\b",
        replacement="[PATIENT_ID_REDACTED]",
    ),
    # Healthcare provider names with titles
    RedactionRule(
        rule_id="phi_physician_name",
        pattern=r"\b(?:Dr\.|Doctor|Physician|Nurse)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        replacement="[PHYSICIAN_REDACTED]",
    ),
]

FINANCIAL_RULES = [
    # Bank account numbers (simple pattern)
    RedactionRule(
        rule_id="financial_account",
        pattern=r"\b(?:account|acct)[\s#:]*(\d{8,17})\b",
        replacement="[ACCOUNT_REDACTED]",
    ),
    # Routing numbers
    RedactionRule(
        rule_id="financial_routing",
        pattern=r"\b(?:routing)[\s#:]*(\d{9})\b",
        replacement="[ROUTING_REDACTED]",
    ),
]


class Redactor:
    """
    Deterministic PII/PHI/financial data redactor.
    Supports field-specific and pattern-based redaction.
    """

    def __init__(self, rules: List[RedactionRule] = None, salt: str = "raia-default-salt"):
        """
        Initialize redactor with rules.

        Args:
            rules: List of redaction rules. If None, uses DEFAULT_PII_RULES.
            salt: Salt for deterministic hashing of sensitive values.
        """
        self.rules = rules or DEFAULT_PII_RULES
        self.salt = salt

    @classmethod
    def for_domain(cls, domain: str, salt: str = "raia-default-salt") -> "Redactor":
        """Create redactor with domain-specific rulesets."""
        rules = DEFAULT_PII_RULES.copy()

        if domain == "healthcare":
            rules.extend(PHI_RULES)
        elif domain in ["banking", "insurance"]:
            rules.extend(FINANCIAL_RULES)

        return cls(rules=rules, salt=salt)

    def redact(self, event: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Redact sensitive data from event.

        Returns:
            Tuple of (redacted_event, redaction_metadata)
        """
        redacted_fields = []
        applied_rules = []

        def redact_recursive(obj: Any, path: str = "") -> Any:
            """Recursively redact object."""
            if isinstance(obj, dict):
                return {k: redact_recursive(v, f"{path}.{k}" if path else k) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [redact_recursive(item, f"{path}[{i}]") for i, item in enumerate(obj)]
            elif isinstance(obj, str):
                return self._redact_string(obj, path, redacted_fields, applied_rules)
            else:
                return obj

        redacted_event = redact_recursive(event)

        redaction_metadata = {
            "applied": len(redacted_fields) > 0,
            "fields": redacted_fields,
            "rule_ids": list(set(applied_rules)),
        }

        return redacted_event, redaction_metadata

    def _redact_string(
        self,
        text: str,
        field_path: str,
        redacted_fields: List[str],
        applied_rules: List[str],
    ) -> str:
        """Redact a single string value."""
        original = text

        for rule in self.rules:
            # Check if rule applies to this field
            if rule.fields and not any(f in field_path for f in rule.fields):
                continue

            # Apply pattern
            if rule.compiled_pattern.search(text):
                if rule.hash_match:
                    # Replace with deterministic hash
                    def hash_replacement(match):
                        value = match.group(0)
                        hashed = self._deterministic_hash(value)
                        return f"[REDACTED_{hashed[:8]}]"

                    text = rule.compiled_pattern.sub(hash_replacement, text)
                else:
                    text = rule.compiled_pattern.sub(rule.replacement, text)

                if text != original:
                    redacted_fields.append(field_path)
                    applied_rules.append(rule.rule_id)

        return text

    def _deterministic_hash(self, value: str) -> str:
        """Generate deterministic hash for a value."""
        salted = f"{self.salt}:{value}"
        return hashlib.sha256(salted.encode("utf-8")).hexdigest()

    def add_rule(self, rule: RedactionRule) -> None:
        """Add a custom redaction rule."""
        self.rules.append(rule)

    def add_custom_pattern(
        self,
        rule_id: str,
        pattern: str,
        replacement: str = "[REDACTED]",
        fields: List[str] = None,
    ) -> None:
        """Convenience method to add a custom regex pattern."""
        self.add_rule(
            RedactionRule(
                rule_id=rule_id,
                pattern=pattern,
                replacement=replacement,
                fields=fields,
            )
        )


# Convenience function for quick redaction
def redact_event(
    event: Dict[str, Any],
    domain: str = "general",
    custom_rules: List[RedactionRule] = None,
) -> Dict[str, Any]:
    """
    Quick redaction helper.

    Args:
        event: Event dict to redact
        domain: Domain for preset rules (healthcare, banking, etc.)
        custom_rules: Additional custom rules

    Returns:
        Redacted event dict
    """
    redactor = Redactor.for_domain(domain)
    if custom_rules:
        redactor.rules.extend(custom_rules)

    redacted_event, _ = redactor.redact(event)
    return redacted_event
