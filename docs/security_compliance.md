# Security, Compliance & Data Lifecycle

## Overview

RAIA is designed with enterprise security and compliance requirements at its core, supporting regulated industries including healthcare (HIPAA), financial services (SOC 2, PCI DSS), and public sector (FedRAMP).

---

## 1. Security Architecture

### 1.1 Defense in Depth

```
┌─────────────────────────────────────┐
│   Network Security (TLS 1.3)       │
├─────────────────────────────────────┤
│   Authentication (API Key/mTLS)     │
├─────────────────────────────────────┤
│   Authorization (RBAC)              │
├─────────────────────────────────────┤
│   Data Validation (Schema Check)    │
├─────────────────────────────────────┤
│   Integrity (HMAC Signing)          │
├─────────────────────────────────────┤
│   Encryption at Rest (AES-256)      │
├─────────────────────────────────────┤
│   Audit Logging                     │
└─────────────────────────────────────┘
```

### 1.2 Transport Security

**TLS Configuration (Minimum)**:
- Protocol: TLS 1.2+ (TLS 1.3 recommended)
- Cipher Suites: Only AEAD ciphers (e.g., AES-GCM, ChaCha20-Poly1305)
- Certificate: Valid, non-self-signed from trusted CA
- HSTS: Enabled with `max-age=31536000; includeSubDomains`

**mTLS (Mutual TLS)** for high-security environments:
```yaml
# Ingestion service configuration
tls:
  enabled: true
  cert_file: /certs/server.crt
  key_file: /certs/server.key
  ca_file: /certs/ca.crt
  client_auth: require  # Require client certificates
```

### 1.3 Authentication

**API Key Authentication**:
- Keys stored as hashed values (bcrypt, cost factor 12)
- Rotated every 90 days (automated)
- Scoped to tenant/project
- Rate-limited per key (default: 1000 req/min)

Example API key structure:
```
raia_<version>_<tenant>_<random_32_chars>
raia_v1_acme_8f3a7b2c9d1e4f5a6b7c8d9e0f1a2b3c
```

**HMAC Signature Verification**:
- Algorithm: HMAC-SHA256
- Signature covers entire event payload (canonical JSON)
- Prevents tampering and replay attacks
- Secret rotation supported without downtime

Python SDK signing:
```python
from raia import EventSigner

signer = EventSigner(secret=os.getenv('RAIA_HMAC_SECRET'))
signature = signer.sign(event)
event['_signature'] = signature
```

### 1.4 Authorization (RBAC)

**Roles**:

| Role | Permissions | Use Case |
|------|-------------|----------|
| `admin` | Full access (read, write, delete, config) | Platform administrators |
| `writer` | Write events, read own tenant data | Ingestion services, SDKs |
| `reader` | Read own tenant data, query metrics | Analytics, dashboards |
| `auditor` | Read all tenants (audit trail only) | Compliance auditors |
| `developer` | Read/write dev/staging only | Development teams |

**Permission Matrix**:

| Resource | admin | writer | reader | auditor | developer |
|----------|-------|--------|--------|---------|-----------|
| POST /ingest | ✓ | ✓ | ✗ | ✗ | ✓ (dev only) |
| GET /metrics | ✓ | ✗ | ✓ | ✓ | ✓ (dev only) |
| GET /events | ✓ | ✗ | ✓ | ✓ | ✓ (dev only) |
| DELETE /events | ✓ | ✗ | ✗ | ✗ | ✗ |
| POST /config | ✓ | ✗ | ✗ | ✗ | ✗ |

**Tenant Isolation**:
- Every request scoped to `tenant` and `project`
- Row-level security (RLS) in Postgres
- Separate Kafka topics per tenant (optional)
- API keys are tenant-specific

Postgres RLS policy:
```sql
CREATE POLICY tenant_isolation ON raia_events
  FOR ALL
  USING (tenant = current_setting('raia.tenant', true));
```

### 1.5 Encryption

**At Rest**:
- Database: Transparent Data Encryption (TDE) or column-level encryption for sensitive fields
- Files: AES-256-GCM encryption for NDJSON files
- Backups: Encrypted with separate key (AWS KMS, Google Cloud KMS, or HashiCorp Vault)

**In Transit**:
- TLS 1.2+ for all network traffic
- No plaintext credentials in logs or environment variables (use secrets manager)

**Key Management**:
- Separate encryption keys per tenant (recommended for regulated industries)
- Key rotation every 365 days (automated)
- Master key stored in HSM or KMS
- DEK (Data Encryption Keys) wrapped by KEK (Key Encryption Key)

---

## 2. PII/PHI Redaction

### 2.1 Redaction Rules

**Default PII Patterns**:
- Email addresses
- Phone numbers (US)
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses

**PHI Patterns** (HIPAA):
- Medical Record Numbers (MRN)
- Patient IDs
- Provider names with titles (Dr., Physician, etc.)

**Financial Patterns**:
- Bank account numbers
- Routing numbers
- Tax IDs

### 2.2 Redaction Strategy

**SDK-Side Redaction** (Recommended):
```python
from raia import Redactor

redactor = Redactor.for_domain('healthcare')
redactor.add_custom_pattern(
    rule_id='custom_patient_id',
    pattern=r'\bPT-\d{6}\b',
    replacement='[PATIENT_ID_REDACTED]'
)

emitter = EventEmitter(config, redactor=redactor)
```

**Server-Side Redaction** (Defense in Depth):
- Ingestion service validates redaction metadata
- Re-applies redaction if `redaction.applied = false`
- Logs redaction failures to audit trail

### 2.3 Deterministic Hashing

For analytics on redacted data without revealing PII:
```python
# Instead of "[REDACTED]", use deterministic hash
RedactionRule(
    rule_id='pii_email_hash',
    pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    hash_match=True  # Generates [REDACTED_a1b2c3d4]
)
```

---

## 3. Audit Logging

### 3.1 Audit Events

All security-relevant actions logged:
- Authentication attempts (success/failure)
- Authorization denials
- Data access (who, what, when, from where)
- Configuration changes
- Data deletion requests (GDPR/CCPA)
- Encryption key operations

### 3.2 Audit Log Schema

```sql
CREATE TABLE raia_audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW(),
    action TEXT NOT NULL,  -- e.g., 'data_access', 'config_change'
    actor_id TEXT,         -- User or service account
    actor_type TEXT,       -- 'human', 'service'
    tenant TEXT NOT NULL,
    project TEXT,
    resource_type TEXT,    -- 'event', 'metric', 'config'
    resource_id TEXT,      -- Specific resource ID
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN,
    error_message TEXT,
    metadata JSONB         -- Additional context
);

CREATE INDEX idx_audit_ts ON raia_audit_log(ts DESC);
CREATE INDEX idx_audit_actor ON raia_audit_log(actor_id, ts DESC);
```

### 3.3 Audit Retention

- **Production**: 7 years (compliance requirement for healthcare/finance)
- **Non-Production**: 1 year
- **Immutable**: Audit logs cannot be modified or deleted (append-only)
- **Offsite Backup**: Daily backups to separate storage account

---

## 4. Compliance Certifications

### 4.1 HIPAA (Healthcare)

**Requirements**:
- ✅ PHI redaction (automatic via SDK)
- ✅ Access controls (RBAC)
- ✅ Audit trails (all PHI access logged)
- ✅ Encryption at rest and in transit
- ✅ BAA (Business Associate Agreement) with cloud provider
- ✅ Breach notification procedures

**HIPAA-Specific Configuration**:
```yaml
# Deploy with HIPAA mode
compliance_mode: hipaa
data_residency: us-only
pii_redaction: mandatory
audit_log_retention: 7y
encryption_at_rest: required
```

### 4.2 SOC 2 Type II

**Control Objectives**:
- **Security**: Access controls, encryption, vulnerability management
- **Availability**: 99.9% uptime SLO, disaster recovery
- **Processing Integrity**: Schema validation, HMAC signing
- **Confidentiality**: Tenant isolation, encryption
- **Privacy**: GDPR compliance, data subject rights

### 4.3 GDPR (EU)

**Data Subject Rights**:
1. **Right to Access**: Export all data for a user
   ```bash
   ./replay_compute.py events.ndjson --filter user_id=<user_id> --export export.json
   ```

2. **Right to Erasure** ("Right to be Forgotten"):
   ```sql
   DELETE FROM raia_events WHERE user_id = '<user_id>';
   INSERT INTO raia_audit_log (action, metadata) VALUES ('gdpr_deletion', '{"user_id": "<user_id>"}');
   ```

3. **Right to Data Portability**: Export in machine-readable format (JSON, CSV, Parquet)

4. **Right to Rectification**: Update incorrect personal data

**Data Processing Agreement (DPA)**:
- RAIA acts as data processor
- Customer is data controller
- Subprocessors (cloud providers) listed in DPA

### 4.4 Data Residency

**Region-Specific Deployment**:
```yaml
# EU deployment (GDPR compliance)
regions:
  - name: eu-west-1
    allowed_tenants: ['eu_customers']
    data_transfer: block_non_eu

# US deployment
regions:
  - name: us-east-1
    allowed_tenants: ['us_customers']
```

**Cross-Border Data Transfer**:
- Standard Contractual Clauses (SCC) for EU → US
- Data localization for regulated industries (healthcare, finance)

---

## 5. Data Lifecycle Management

### 5.1 Retention Policies

**Default Retention**:
```yaml
retention_policies:
  events:
    hot_storage: 30d    # Fast query access
    cold_storage: 365d  # Archived, slower access
    delete_after: 1095d # 3 years (configurable)

  metrics:
    raw: 30d            # Delete raw events after aggregation
    hourly_agg: 365d
    daily_agg: 1095d    # Keep aggregates longer

  audit_logs:
    retention: 2555d    # 7 years (compliance)
    immutable: true
```

**Tenant-Specific Retention**:
```yaml
# Premium tier: longer retention
tenants:
  acme_corp:
    retention_days: 730  # 2 years
  startup_xyz:
    retention_days: 90   # 3 months
```

### 5.2 Data Deletion

**Automated Deletion** (via cron or k8s CronJob):
```bash
# Daily job to drop old Postgres partitions
0 2 * * * psql -c "SELECT drop_old_partitions(90);"  # Drop data older than 90 days
```

**Manual Deletion** (GDPR/CCPA request):
```python
# Delete specific user's data
from raia.admin import delete_user_data

delete_user_data(
    user_id='usr_12345',
    reason='gdpr_request',
    requested_by='privacy_officer@acme.com'
)
```

### 5.3 Data Archival

**Cold Storage Migration**:
- After 30 days, move to S3 Glacier or Azure Cool Blob
- Compressed (gzip) and encrypted
- Indexed in metadata DB for retrieval

**Archive Format**:
```
s3://raia-archive/{tenant}/{year}/{month}/{day}/events-{partition}.ndjson.gz.enc
```

---

## 6. Secret Management

### 6.1 Secrets Never in Code

❌ **Bad**:
```python
HMAC_SECRET = "mysecretkey123"  # NEVER do this
```

✅ **Good**:
```python
import os
HMAC_SECRET = os.getenv('RAIA_HMAC_SECRET')
if not HMAC_SECRET:
    raise ValueError("RAIA_HMAC_SECRET not set")
```

### 6.2 Secrets Manager Integration

**AWS Secrets Manager**:
```python
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='raia/hmac_secret')
HMAC_SECRET = response['SecretString']
```

**HashiCorp Vault**:
```python
import hvac

client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.v2.read_secret_version(path='raia/hmac_secret')
HMAC_SECRET = secret['data']['data']['value']
```

### 6.3 Secret Rotation

**Automated Rotation** (every 90 days):
1. Generate new secret
2. Deploy new secret alongside old (dual-support window)
3. Update SDK configs to use new secret
4. After 7 days, revoke old secret

---

## 7. Incident Response

### 7.1 Security Incident Classification

**Severity Levels**:
- **P0 (Critical)**: Data breach, unauthorized access to production, encryption failure
- **P1 (High)**: Vulnerability exploitation attempt, DDoS, auth bypass
- **P2 (Medium)**: Suspicious activity, failed auth spikes, config drift
- **P3 (Low)**: False positive alerts, minor policy violations

### 7.2 Incident Response Playbook

**Data Breach Response**:
1. **Detect**: Audit logs show unauthorized data access
2. **Contain**: Revoke compromised API keys, isolate affected tenants
3. **Investigate**: Determine scope (what data, how many users, time window)
4. **Notify**:
   - Affected customers within 24h
   - Regulators (HHS for HIPAA, ICO for GDPR) within 72h
5. **Remediate**: Patch vulnerability, rotate all secrets
6. **Post-Mortem**: Document root cause, implement preventive measures

**Breach Notification Template**:
```
Subject: Security Incident Notification - <Incident ID>

Dear <Customer>,

We are writing to inform you of a security incident affecting your RAIA
deployment. On <date>, we detected unauthorized access to event data for
tenant <tenant_id> covering the period <start_date> to <end_date>.

Data exposed: <list of data types, e.g., "session IDs, agent logs">
PII exposed: <Yes/No - if yes, specify types>

Actions taken:
- Revoked compromised credentials
- Implemented additional access controls
- Enhanced monitoring

Recommended actions for you:
- Review audit logs for suspicious activity
- Rotate API keys
- Notify affected end-users if PII was exposed

For questions, contact security@raia.ai or call +1-555-SECURITY.

Sincerely,
RAIA Security Team
```

---

## 8. Compliance Checklist

### Pre-Deployment Checklist

- [ ] TLS 1.2+ enabled with valid certificates
- [ ] API keys generated and stored in secrets manager
- [ ] HMAC signing enabled (`RAIA_REQUIRE_SIGNATURE=true`)
- [ ] PII/PHI redaction rules configured for domain
- [ ] RBAC roles assigned to service accounts
- [ ] Tenant isolation tested (cannot access other tenant's data)
- [ ] Encryption at rest enabled (database TDE, file encryption)
- [ ] Audit logging enabled and tested
- [ ] Retention policies configured
- [ ] Backup and disaster recovery tested
- [ ] Monitoring and alerting configured
- [ ] Incident response runbook reviewed
- [ ] Security scanning (SAST/DAST) completed
- [ ] Penetration testing completed (for production)
- [ ] Compliance documentation reviewed (DPA, BAA, SCC)

### Ongoing Compliance

**Monthly**:
- [ ] Review audit logs for anomalies
- [ ] Verify backups are encrypted and restorable
- [ ] Check for expiring certificates

**Quarterly**:
- [ ] Rotate API keys and HMAC secrets
- [ ] Review and update access permissions
- [ ] Conduct tabletop security exercises

**Annually**:
- [ ] External security audit
- [ ] Penetration testing
- [ ] Compliance certification renewal (SOC 2, ISO 27001)
- [ ] Review and update DPA/BAA agreements
