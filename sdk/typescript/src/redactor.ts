/**
 * PII/PHI Redactor for TypeScript
 */

import { RedactionMetadata } from './types';

export interface RedactionRule {
  ruleId: string;
  pattern: RegExp;
  replacement: string;
  fields?: string[]; // Specific fields to apply to (undefined = all strings)
}

// Pre-defined rulesets
export const DEFAULT_PII_RULES: RedactionRule[] = [
  {
    ruleId: 'pii_email',
    pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/gi,
    replacement: '[EMAIL_REDACTED]',
  },
  {
    ruleId: 'pii_phone_us',
    pattern: /\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b/g,
    replacement: '[PHONE_REDACTED]',
  },
  {
    ruleId: 'pii_ssn',
    pattern: /\b\d{3}-\d{2}-\d{4}\b/g,
    replacement: '[SSN_REDACTED]',
  },
  {
    ruleId: 'pii_credit_card',
    pattern: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g,
    replacement: '[CC_REDACTED]',
  },
  {
    ruleId: 'pii_ip_address',
    pattern: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
    replacement: '[IP_REDACTED]',
  },
];

export const PHI_RULES: RedactionRule[] = [
  {
    ruleId: 'phi_mrn',
    pattern: /\b(?:MRN|mrn|medical record)[\s:]*([A-Z0-9]{6,})\b/gi,
    replacement: '[MRN_REDACTED]',
  },
  {
    ruleId: 'phi_patient_id',
    pattern: /\b(?:patient[_\s]?id|pat[_\s]?id)[\s:]*([A-Z0-9]{6,})\b/gi,
    replacement: '[PATIENT_ID_REDACTED]',
  },
  {
    ruleId: 'phi_physician_name',
    pattern: /\b(?:Dr\.|Doctor|Physician|Nurse)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b/g,
    replacement: '[PHYSICIAN_REDACTED]',
  },
];

export const FINANCIAL_RULES: RedactionRule[] = [
  {
    ruleId: 'financial_account',
    pattern: /\b(?:account|acct)[\s#:]*(\d{8,17})\b/gi,
    replacement: '[ACCOUNT_REDACTED]',
  },
  {
    ruleId: 'financial_routing',
    pattern: /\b(?:routing)[\s#:]*(\d{9})\b/gi,
    replacement: '[ROUTING_REDACTED]',
  },
];

export class Redactor {
  private rules: RedactionRule[];

  constructor(rules?: RedactionRule[]) {
    this.rules = rules ?? DEFAULT_PII_RULES;
  }

  static forDomain(domain: string): Redactor {
    let rules = [...DEFAULT_PII_RULES];

    if (domain === 'healthcare') {
      rules = rules.concat(PHI_RULES);
    } else if (domain === 'banking' || domain === 'insurance') {
      rules = rules.concat(FINANCIAL_RULES);
    }

    return new Redactor(rules);
  }

  redact(event: any): [any, RedactionMetadata] {
    const redactedFields: string[] = [];
    const appliedRules: string[] = [];

    const redactRecursive = (obj: any, path: string = ''): any => {
      if (typeof obj === 'string') {
        return this.redactString(obj, path, redactedFields, appliedRules);
      } else if (Array.isArray(obj)) {
        return obj.map((item, i) => redactRecursive(item, `${path}[${i}]`));
      } else if (obj !== null && typeof obj === 'object') {
        const result: any = {};
        for (const [key, value] of Object.entries(obj)) {
          const fieldPath = path ? `${path}.${key}` : key;
          result[key] = redactRecursive(value, fieldPath);
        }
        return result;
      }
      return obj;
    };

    const redactedEvent = redactRecursive(event);

    const metadata: RedactionMetadata = {
      applied: redactedFields.length > 0,
      fields: redactedFields,
      rule_ids: Array.from(new Set(appliedRules)),
    };

    return [redactedEvent, metadata];
  }

  private redactString(
    text: string,
    fieldPath: string,
    redactedFields: string[],
    appliedRules: string[]
  ): string {
    let result = text;

    for (const rule of this.rules) {
      // Check if rule applies to this field
      if (rule.fields && !rule.fields.some((f) => fieldPath.includes(f))) {
        continue;
      }

      if (rule.pattern.test(result)) {
        result = result.replace(rule.pattern, rule.replacement);
        redactedFields.push(fieldPath);
        appliedRules.push(rule.ruleId);
      }
    }

    return result;
  }

  addRule(rule: RedactionRule): void {
    this.rules.push(rule);
  }
}
