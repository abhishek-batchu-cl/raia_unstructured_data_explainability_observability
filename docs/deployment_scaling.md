# Deployment & Scaling Guidance

## Deployment Architecture

### Small Scale (< 1M events/day)
- **Ingestion**: 2-3 pods (2 vCPU, 2GB RAM each)
- **Storage**: Single Postgres instance or NDJSON files
- **Cost**: ~$200-500/month

### Medium Scale (1M - 100M events/day)
- **Ingestion**: 5-10 pods with HPA (70% CPU target)
- **Storage**: Postgres with read replicas or Kafka cluster (3 brokers)
- **Caching**: Redis for hot metrics
- **Cost**: ~$2K-10K/month

### Large Scale (> 100M events/day)
- **Ingestion**: 20+ pods across multiple regions
- **Storage**: Kafka (9+ brokers) + S3/GCS for cold storage
- **Processing**: Spark/Flink for real-time aggregation
- **Cost**: $20K+/month

## Scaling Strategies

### Horizontal Scaling (Recommended)
Scale out ingestion pods based on:
- CPU utilization (target: 70%)
- Memory (target: 80%)
- Queue depth (target: < 1000 events)
- Custom metric: `raia_events_received_total` rate

### Vertical Scaling
Increase pod resources when:
- High GC pressure (JVM-based services)
- Large batch sizes requiring more memory

### Storage Scaling

**Postgres**:
- Partition tables by time (monthly recommended)
- Use connection pooling (PgBouncer)
- Read replicas for analytics queries
- Autovacuum tuning for high write throughput

**Kafka**:
- Increase partitions (1 partition per 10MB/s write throughput)
- Replication factor: 3 for prod
- Retention: 7 days (adjust based on replay needs)

## Capacity Planning

### Event Rate Estimation
```
events_per_day = sessions_per_day × avg_events_per_session
Example: 100K sessions × 15 events = 1.5M events/day
```

### Storage Requirements
```
daily_storage_gb = events_per_day × avg_event_size_kb / 1024 / 1024
Example: 1.5M × 2KB = 3GB/day = 90GB/month (raw)
With compression (4:1): ~23GB/month
```

### Compute Requirements
```
cpu_cores = (events_per_second × processing_time_ms) / 1000
Example: 50 events/sec × 5ms = 0.25 cores (add 3x buffer = 1 core)
```

## Backpressure Handling

When ingestion rate exceeds processing capacity:

1. **SDK-side**: Circuit breaker opens, falls back to local file
2. **Queue**: Events buffer in memory queue (max 10K)
3. **Alerts**: High queue depth triggers scaling
4. **Shedding**: Reject new events with HTTP 503 (prefer this over data loss)

## Disaster Recovery

### Backup Strategy
- **Postgres**: Daily full backup + WAL archiving
- **NDJSON**: Replicate to S3 with versioning
- **Retention**: 30 days for backups

### Recovery Time Objective (RTO)
- Target: < 1 hour for complete service restoration

### Recovery Point Objective (RPO)
- Target: < 5 minutes of data loss (use WAL shipping)

## Multi-Region Deployment

Active-Active for global low latency:
```
        ┌──────────────┐
        │   Route 53   │
        │ (GeoDNS)     │
        └──────┬───────┘
               │
        ┌──────┴───────┐
        │              │
   ┌────▼────┐   ┌────▼────┐
   │ US-EAST │   │ EU-WEST │
   │ Cluster │   │ Cluster │
   └────┬────┘   └────┬────┘
        │              │
        └──────┬───────┘
               ▼
      ┌─────────────────┐
      │  Central Store  │
      │  (S3 / Kafka)   │
      └─────────────────┘
```

## Cost Optimization

- Use spot instances for non-critical workloads
- Compress old data (gzip: 4:1 ratio)
- Archive to cold storage after 30 days
- Sample non-critical events (e.g., 10% sampling for dev)
