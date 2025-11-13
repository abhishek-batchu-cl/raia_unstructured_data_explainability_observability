"""
Event signer using HMAC-SHA256 for tamper detection.
"""

import hashlib
import hmac
import json
from typing import Any, Dict


class EventSigner:
    """HMAC-SHA256 signer for event integrity."""

    def __init__(self, secret: str):
        """
        Initialize signer with secret key.

        Args:
            secret: HMAC secret key
        """
        if not secret:
            raise ValueError("HMAC secret cannot be empty")
        self.secret = secret.encode("utf-8")

    def sign(self, event: Dict[str, Any]) -> str:
        """
        Generate HMAC signature for event.

        Args:
            event: Event dict to sign

        Returns:
            Hex-encoded HMAC signature
        """
        canonical = self._canonicalize(event)
        signature = hmac.new(self.secret, canonical.encode("utf-8"), hashlib.sha256)
        return signature.hexdigest()

    def verify(self, event: Dict[str, Any], signature: str) -> bool:
        """
        Verify event signature.

        Args:
            event: Event dict
            signature: Hex-encoded signature to verify

        Returns:
            True if signature is valid
        """
        expected = self.sign(event)
        return hmac.compare_digest(expected, signature)

    def _canonicalize(self, event: Dict[str, Any]) -> str:
        """
        Create canonical string representation for signing.
        Excludes _signature field and sorts keys for determinism.
        """
        # Remove signature field if present
        event_copy = {k: v for k, v in event.items() if k != "_signature"}

        # Sort keys recursively for determinism
        return json.dumps(event_copy, sort_keys=True, separators=(",", ":"))


def sign_event(event: Dict[str, Any], secret: str) -> Dict[str, Any]:
    """
    Convenience function to sign an event and add signature field.

    Args:
        event: Event to sign
        secret: HMAC secret

    Returns:
        Event with _signature field added
    """
    signer = EventSigner(secret)
    signature = signer.sign(event)
    event["_signature"] = signature
    return event


def verify_event(event: Dict[str, Any], secret: str) -> bool:
    """
    Convenience function to verify event signature.

    Args:
        event: Event with _signature field
        secret: HMAC secret

    Returns:
        True if signature is valid
    """
    if "_signature" not in event:
        return False

    signature = event["_signature"]
    signer = EventSigner(secret)
    return signer.verify(event, signature)
