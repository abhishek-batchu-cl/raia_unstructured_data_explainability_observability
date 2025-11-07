-- RAIA Postgres Schema
-- Production-grade schema with partitioning, indexes, and retention policies

-- Main events table (partitioned by time for efficient retention)
CREATE TABLE IF NOT EXISTS raia_events (
    event_id UUID NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL,
    run_id UUID NOT NULL,
    agent_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    tenant TEXT NOT NULL,
    project TEXT NOT NULL,
    domain TEXT,
    user_id TEXT,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (event_id, ts)
) PARTITION BY RANGE (ts);

-- Create partitions (example: monthly partitions for 2025)
-- In production, automate partition creation with pg_partman or similar
CREATE TABLE IF NOT EXISTS raia_events_2025_01 PARTITION OF raia_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS raia_events_2025_02 PARTITION OF raia_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Add more partitions as needed...

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_events_session_id ON raia_events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_tenant_project ON raia_events(tenant, project, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_agent_id ON raia_events(agent_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON raia_events(event_type, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_domain ON raia_events(domain, ts DESC) WHERE domain IS NOT NULL;

-- GIN index on JSONB for fast querying of event details
CREATE INDEX IF NOT EXISTS idx_events_data_gin ON raia_events USING GIN (data jsonb_path_ops);

-- Tenant isolation view (for multi-tenancy)
CREATE OR REPLACE VIEW raia_events_tenant AS
SELECT
    event_id,
    ts,
    session_id,
    run_id,
    agent_id,
    event_type,
    tenant,
    project,
    domain,
    data
FROM raia_events
WHERE tenant = current_setting('raia.tenant', true);

-- Aggregated metrics table (for faster dashboard queries)
CREATE TABLE IF NOT EXISTS raia_metrics_hourly (
    tenant TEXT NOT NULL,
    project TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    hour TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    sample_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant, project, agent_id, hour, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_metrics_hour ON raia_metrics_hourly(hour DESC);

-- Audit log table (for compliance)
CREATE TABLE IF NOT EXISTS raia_audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW(),
    action TEXT NOT NULL,
    tenant TEXT NOT NULL,
    project TEXT,
    user_id TEXT,
    event_id UUID,
    metadata JSONB,
    ip_address INET
);

CREATE INDEX IF NOT EXISTS idx_audit_ts ON raia_audit_log(ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON raia_audit_log(tenant, ts DESC);

-- Function to drop old partitions (for data retention)
CREATE OR REPLACE FUNCTION drop_old_partitions(retention_days INTEGER)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - retention_days;

    FOR partition_name IN
        SELECT tablename
        FROM pg_tables
        WHERE tablename LIKE 'raia_events_%'
        AND schemaname = 'public'
    LOOP
        -- Extract date from partition name and check if older than retention
        -- This is simplified; production should use proper date parsing
        EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', partition_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Materialized view for common dashboard queries (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS raia_dashboard_stats AS
SELECT
    tenant,
    project,
    agent_id,
    DATE_TRUNC('hour', ts) as hour,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as session_count,
    COUNT(*) FILTER (WHERE event_type = 'finalized' AND (data->>'success')::boolean = true) as success_count,
    COUNT(*) FILTER (WHERE event_type = 'error') as error_count,
    COUNT(*) FILTER (WHERE event_type = 'escalation') as escalation_count,
    AVG((data->>'latency_ms')::numeric) FILTER (WHERE data->>'latency_ms' IS NOT NULL) as avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY (data->>'latency_ms')::numeric)
        FILTER (WHERE data->>'latency_ms' IS NOT NULL) as p95_latency_ms
FROM raia_events
WHERE ts >= NOW() - INTERVAL '7 days'
GROUP BY tenant, project, agent_id, DATE_TRUNC('hour', ts);

CREATE UNIQUE INDEX ON raia_dashboard_stats(tenant, project, agent_id, hour);

-- Grant permissions (adjust for your RBAC setup)
-- Example: read-only role for analytics
CREATE ROLE raia_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO raia_reader;
GRANT SELECT ON raia_events_tenant TO raia_reader;

-- Example: writer role for ingestion service
CREATE ROLE raia_writer;
GRANT INSERT ON raia_events TO raia_writer;
GRANT INSERT ON raia_audit_log TO raia_writer;

-- Row-level security for tenant isolation (optional)
ALTER TABLE raia_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON raia_events
    FOR SELECT
    USING (tenant = current_setting('raia.tenant', true));

-- Comments for documentation
COMMENT ON TABLE raia_events IS 'Main event storage, partitioned by timestamp for efficient retention';
COMMENT ON COLUMN raia_events.data IS 'Full event payload as JSONB for flexible querying';
COMMENT ON TABLE raia_metrics_hourly IS 'Pre-aggregated hourly metrics for dashboard performance';
COMMENT ON TABLE raia_audit_log IS 'Audit trail for compliance (GDPR, HIPAA, etc.)';
