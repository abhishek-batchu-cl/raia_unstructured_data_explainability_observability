# Embedding Drift Detection in RAIA

## Overview

RAIA's embedding drift detection properly compares **two embedding datasets** to detect distribution shifts that could degrade RAG system performance.

## How It Works

### 1. Two-Dataset Comparison

```python
# Baseline embeddings (v1.0) - 1000 documents, 1536 dimensions
baseline_embeddings = generate_embeddings(documents, model="v1.0")

# Current embeddings (v1.1) - same documents, potentially different distribution
current_embeddings = generate_embeddings(documents, model="v1.1")
```

### 2. Drift Metrics Computed

#### a) **KL Divergence** (Kullback-Leibler)
- Measures how one probability distribution diverges from another
- Non-symmetric: KL(P||Q) ≠ KL(Q||P)
- Higher values = more drift
- **Threshold**: 0.10 (configurable)

```python
kl_divergence = entropy(current_hist, baseline_hist)
# Result: 0.2221 → DRIFT DETECTED ⚠️
```

#### b) **JS Divergence** (Jensen-Shannon)
- Symmetric version of KL divergence
- Range: [0, 1]
- More stable than KL divergence

```python
m = 0.5 * (baseline_hist + current_hist)
js_divergence = 0.5 * entropy(baseline_hist, m) + 0.5 * entropy(current_hist, m)
# Result: 0.0641
```

#### c) **Wasserstein Distance** (Earth Mover's Distance)
- Measures minimum "cost" to transform one distribution to another
- Robust to outliers
- Considers the geometry of the embedding space

```python
wasserstein_distance = scipy_wasserstein(baseline_proj, current_proj)
# Result: 0.0093
```

#### d) **Cosine Similarity Drift**
- Per-pair cosine similarity between corresponding embeddings
- Measures angular change in embedding direction

```python
cosine_drift_mean = 1 - mean([cosine_sim(base[i], curr[i]) for i in range(n)])
# Result: 0.5949 → High drift!
```

#### e) **Euclidean Distance**
- L2 distance between corresponding embeddings
- Measures magnitude of embedding shift

```python
euclidean_drift_mean = mean([euclidean(base[i], curr[i]) for i in range(n)])
# Result: 1.0906
```

## Example Output

```bash
4.5 Tracking embedding drift...
  → Generating baseline embeddings (v1.0, n=1000)...
  → Generating current embeddings (v1.1, n=1000)...
  → Computing drift metrics...
  → Computed KL divergence: 0.2221
  → Computed JS divergence: 0.0641
  → Computed Wasserstein distance: 0.0093
  → Mean cosine drift: 0.5949
  → Mean Euclidean distance: 1.0906
  ✅ ⚠️  DRIFT DETECTED: KL=0.2221, JS=0.0641, n=1000
```

## Drift Detection Logic

```python
drift_threshold = 0.10
is_drifting = kl_divergence > drift_threshold

# In this case:
# 0.2221 > 0.10 → DRIFT DETECTED ⚠️
```

## Real-World Use Cases

### 1. Model Version Changes
```python
# Baseline: text-embedding-ada-002 (v1.0)
baseline = embed_documents(docs, model="text-embedding-ada-002")

# Current: text-embedding-ada-002 (v2.0) - model was updated
current = embed_documents(docs, model="text-embedding-ada-002-v2")

# Detect drift to understand impact of model update
drift = compute_drift(baseline, current)
```

### 2. Data Distribution Shift
```python
# Baseline: Documents from January 2024
baseline = embed_documents(docs_jan_2024, model="ada-002")

# Current: Documents from June 2024 - topic distribution changed
current = embed_documents(docs_jun_2024, model="ada-002")

# Detect if document topics have shifted
drift = compute_drift(baseline, current)
```

### 3. Fine-Tuning Impact
```python
# Baseline: Pre-trained model
baseline = embed_documents(docs, model="base-model")

# Current: Fine-tuned model
current = embed_documents(docs, model="fine-tuned-model")

# Measure how much fine-tuning shifted embeddings
drift = compute_drift(baseline, current)
```

## Why This Matters for RAG

### Impact on Retrieval Quality

When embeddings drift:

1. **Relevance Degradation**
   - Documents that were similar (high cosine similarity) may become dissimilar
   - Retrieval quality drops

2. **Index Invalidation**
   - Vector index built with v1.0 embeddings
   - Queries use v1.1 embeddings
   - Mismatch causes poor retrieval

3. **Inconsistent Results**
   - Same query at different times returns different results
   - User experience degrades

### Mitigation Strategies

When drift is detected:

```python
if drift_detected:
    # Option 1: Re-embed all documents with new model
    reindex_documents(documents, new_model)

    # Option 2: Use drift-aware retrieval
    adjust_similarity_threshold(drift_magnitude)

    # Option 3: Maintain multiple indexes
    hybrid_search(index_v1, index_v2, weights=[0.7, 0.3])
```

## Database Schema

```sql
CREATE TABLE raia_embedding_drift_metrics (
    id INTEGER PRIMARY KEY,
    index_name TEXT NOT NULL,

    -- Drift metrics
    kl_divergence REAL,
    js_divergence REAL,
    wasserstein_distance REAL,
    cosine_drift_mean REAL,
    euclidean_drift_mean REAL,

    -- Detection
    drift_threshold REAL,
    is_drifting BOOLEAN,

    -- Metadata
    samples_compared INTEGER,
    timestamp DATETIME,
    metadata TEXT
);
```

## Query Example

```sql
SELECT
    index_name,
    kl_divergence,
    js_divergence,
    is_drifting,
    samples_compared
FROM raia_embedding_drift_metrics
WHERE is_drifting = 1
ORDER BY kl_divergence DESC;
```

## Statistical Significance

For robust drift detection, we recommend:

- **Minimum samples**: 100 embedding pairs
- **Recommended samples**: 1000+ embedding pairs
- **Statistical test**: Kolmogorov-Smirnov test for distribution comparison

```python
from scipy.stats import ks_2samp

# Additional statistical test
ks_statistic, p_value = ks_2samp(baseline_proj, current_proj)

if p_value < 0.05:
    print("Distributions are significantly different (p < 0.05)")
```

## Best Practices

1. **Establish Baseline Early**
   - Capture embeddings when system is known to be working well
   - Store baseline embeddings or compute summary statistics

2. **Regular Monitoring**
   - Run drift detection weekly or after model updates
   - Track drift over time to identify trends

3. **Multiple Metrics**
   - Don't rely on a single metric
   - KL divergence + Cosine drift + Wasserstein = robust detection

4. **Context-Aware Thresholds**
   - Medical/legal domains: Low threshold (0.05)
   - General chat: Higher threshold (0.15)
   - Adjust based on acceptable degradation

5. **Root Cause Analysis**
   - When drift detected, investigate why
   - Model update? Data shift? Code bug?

## Comparison with Alternatives

| Tool | Drift Detection | Methodology |
|------|-----------------|-------------|
| **RAIA** | ✅ Yes | Multi-metric (KL, JS, Wasserstein, cosine) |
| LangSmith | ❌ No | N/A |
| LangFuse | ❌ No | N/A |
| Arize | ✅ Yes | Distribution monitoring |
| WhyLabs | ✅ Yes | Statistical profiling |

## Limitations

1. **Computational Cost**
   - Comparing 1000+ embeddings can be slow
   - Use sampling for large datasets

2. **Baseline Staleness**
   - Baseline may become outdated
   - Periodically update baseline

3. **Multi-Dimensional Complexity**
   - Full 1536-dim comparison is expensive
   - We project to 1D for KL/JS/Wasserstein

## Future Enhancements

- [ ] Automatic baseline update schedule
- [ ] Drift trend visualization
- [ ] Per-topic drift detection
- [ ] Automated mitigation recommendations
- [ ] Integration with vector DB health checks

---

**Summary**: RAIA properly implements embedding drift detection by comparing two embedding datasets and computing multiple statistical metrics to identify when RAG retrieval quality may degrade.
