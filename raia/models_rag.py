"""
RAIA RAG Evaluation - Data Models

Pydantic models for RAG (Retrieval-Augmented Generation) evaluation,
including retrieval quality, answer faithfulness, embedding drift detection,
and vector index health monitoring.

This makes RAIA the ONLY framework with comprehensive RAG + Agent evaluation.
"""

from datetime import datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class RAIARetrievalMetrics(BaseModel):
    """
    Metrics for evaluating retrieval quality in RAG systems.

    Tracks how well the retrieval system finds relevant documents.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    query: str = Field(..., description="User query")
    retrieved_count: int = Field(..., description="Number of documents retrieved")

    # Retrieval Effectiveness Metrics
    precision_at_k: Optional[float] = Field(None, description="Precision@K (0.0-1.0)", ge=0.0, le=1.0)
    recall_at_k: Optional[float] = Field(None, description="Recall@K (0.0-1.0)", ge=0.0, le=1.0)
    mrr: Optional[float] = Field(None, description="Mean Reciprocal Rank", ge=0.0, le=1.0)
    ndcg: Optional[float] = Field(None, description="Normalized Discounted Cumulative Gain", ge=0.0, le=1.0)

    # Performance Metrics
    retrieval_latency_ms: float = Field(..., description="Retrieval latency in milliseconds")
    rerank_latency_ms: Optional[float] = Field(None, description="Reranking latency in milliseconds")
    total_latency_ms: float = Field(..., description="Total latency in milliseconds")

    # Context Quality Metrics
    context_relevance_score: Optional[float] = Field(None, description="Average relevance of retrieved docs (0.0-1.0)", ge=0.0, le=1.0)
    context_diversity: Optional[float] = Field(None, description="Diversity of retrieved docs (0.0-1.0)", ge=0.0, le=1.0)
    context_coverage: Optional[float] = Field(None, description="How well results cover query topic (0.0-1.0)", ge=0.0, le=1.0)

    # Retrieved Documents
    retrieved_doc_ids: List[str] = Field(default_factory=list, description="IDs of retrieved documents")
    relevance_scores: List[float] = Field(default_factory=list, description="Per-document relevance scores")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When metrics were captured")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "query": "What is the capital of France?",
                "retrieved_count": 5,
                "precision_at_k": 0.80,
                "recall_at_k": 0.67,
                "mrr": 0.75,
                "retrieval_latency_ms": 45.2,
                "context_relevance_score": 0.85,
                "retrieved_doc_ids": ["doc1", "doc2", "doc3", "doc4", "doc5"],
                "relevance_scores": [0.95, 0.87, 0.82, 0.65, 0.55]
            }
        }


class RAIAAnswerQualityMetrics(BaseModel):
    """
    Metrics for evaluating answer quality in RAG systems.

    Focuses on faithfulness (grounding in retrieved context) and relevance.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    query: str = Field(..., description="User query")
    answer: str = Field(..., description="Generated answer")

    # Faithfulness Metrics (Critical for RAG)
    answer_faithfulness: Optional[float] = Field(None, description="Is answer grounded in context? (0.0-1.0)", ge=0.0, le=1.0)
    hallucination_score: Optional[float] = Field(None, description="Hallucination score (0=none, 1=full)", ge=0.0, le=1.0)
    citation_accuracy: Optional[float] = Field(None, description="Accuracy of citations/sources (0.0-1.0)", ge=0.0, le=1.0)

    # Answer Quality Metrics
    answer_relevance: Optional[float] = Field(None, description="Does answer address query? (0.0-1.0)", ge=0.0, le=1.0)
    answer_completeness: Optional[float] = Field(None, description="Is answer complete? (0.0-1.0)", ge=0.0, le=1.0)
    answer_conciseness: Optional[float] = Field(None, description="Is answer concise? (0.0-1.0)", ge=0.0, le=1.0)

    # Context Utilization
    context_utilization: Optional[float] = Field(None, description="How much context was used? (0.0-1.0)", ge=0.0, le=1.0)
    context_recall: Optional[float] = Field(None, description="Did answer use all relevant context? (0.0-1.0)", ge=0.0, le=1.0)

    # Contradiction Detection
    self_contradiction: Optional[bool] = Field(None, description="Does answer contradict itself?")
    context_contradiction: Optional[bool] = Field(None, description="Does answer contradict context?")

    # Performance
    generation_latency_ms: Optional[float] = Field(None, description="Answer generation latency in milliseconds")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When metrics were captured")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "query": "What is the capital of France?",
                "answer": "The capital of France is Paris, which is located in the north-central part of the country.",
                "answer_faithfulness": 0.95,
                "hallucination_score": 0.05,
                "answer_relevance": 0.98,
                "context_utilization": 0.80,
                "self_contradiction": False,
                "context_contradiction": False
            }
        }


class RAIAEmbeddingDriftMetrics(BaseModel):
    """
    Metrics for detecting embedding drift over time.

    UNIQUE TO RAIA - No competitor offers comprehensive embedding drift detection!

    Monitors changes in embedding distributions to detect data drift,
    which can degrade RAG system performance.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    index_name: str = Field(..., description="Name of vector index/database")

    # Distribution Statistics
    query_embedding_mean: Optional[List[float]] = Field(None, description="Mean of query embeddings")
    query_embedding_std: Optional[List[float]] = Field(None, description="Std dev of query embeddings")

    # Drift Detection Metrics (compare to baseline)
    kl_divergence: Optional[float] = Field(None, description="KL divergence from baseline", ge=0.0)
    js_divergence: Optional[float] = Field(None, description="Jensen-Shannon divergence", ge=0.0, le=1.0)
    wasserstein_distance: Optional[float] = Field(None, description="Earth mover's distance", ge=0.0)

    # Similarity Metrics
    avg_similarity_to_baseline: Optional[float] = Field(None, description="Avg cosine similarity to baseline", ge=-1.0, le=1.0)
    similarity_distribution_shift: Optional[float] = Field(None, description="Change in similarity distribution", ge=0.0)

    # Drift Status
    drift_detected: bool = Field(False, description="Has drift exceeded threshold?")
    drift_severity: Literal["none", "low", "medium", "high", "critical"] = Field("none", description="Severity level")
    drift_threshold: Optional[float] = Field(None, description="Threshold used for detection")

    # Baseline & Period Info
    baseline_period_start: Optional[datetime] = Field(None, description="Start of baseline period")
    baseline_period_end: Optional[datetime] = Field(None, description="End of baseline period")
    current_period_start: Optional[datetime] = Field(None, description="Start of current period")
    current_period_end: Optional[datetime] = Field(None, description="End of current period")
    samples_analyzed: int = Field(0, description="Number of samples analyzed")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When drift check was performed")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "index_name": "knowledge_base_v1",
                "kl_divergence": 0.045,
                "js_divergence": 0.032,
                "avg_similarity_to_baseline": 0.92,
                "drift_detected": False,
                "drift_severity": "low",
                "samples_analyzed": 1000
            }
        }


class RAIAVectorIndexHealth(BaseModel):
    """
    Metrics for monitoring vector database/index health.

    UNIQUE TO RAIA - No competitor offers vector index health monitoring!

    Tracks performance degradation, recall quality, and resource usage
    of vector databases over time.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    index_name: str = Field(..., description="Name of vector index/database")

    # Index Statistics
    total_documents: int = Field(..., description="Total documents in index")
    total_embeddings: int = Field(..., description="Total embeddings in index")
    index_size_mb: Optional[float] = Field(None, description="Index size in megabytes")

    # Query Performance
    avg_query_latency_ms: float = Field(..., description="Average query latency in milliseconds")
    p50_latency_ms: Optional[float] = Field(None, description="50th percentile latency")
    p95_latency_ms: Optional[float] = Field(None, description="95th percentile latency")
    p99_latency_ms: Optional[float] = Field(None, description="99th percentile latency")

    # Recall Quality (over time)
    avg_recall_at_10: Optional[float] = Field(None, description="Average recall@10", ge=0.0, le=1.0)
    recall_degradation_pct: Optional[float] = Field(None, description="% change in recall from baseline")

    # Index Freshness
    last_updated: datetime = Field(..., description="When index was last updated")
    staleness_hours: float = Field(..., description="Hours since last update")
    pending_updates: int = Field(0, description="Documents waiting to be indexed")

    # Resource Usage
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in megabytes")
    cpu_usage_pct: Optional[float] = Field(None, description="CPU usage percentage")
    disk_usage_mb: Optional[float] = Field(None, description="Disk usage in megabytes")

    # Health Status
    health_status: Literal["healthy", "degraded", "critical"] = Field("healthy", description="Overall health status")
    health_issues: List[str] = Field(default_factory=list, description="List of detected issues")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When health check was performed")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "index_name": "knowledge_base_v1",
                "total_documents": 50000,
                "total_embeddings": 50000,
                "index_size_mb": 2048.5,
                "avg_query_latency_ms": 45.2,
                "p95_latency_ms": 120.5,
                "avg_recall_at_10": 0.87,
                "last_updated": "2024-01-15T10:00:00Z",
                "staleness_hours": 2.5,
                "health_status": "healthy",
                "health_issues": []
            }
        }


class RAIAPipelineMetrics(BaseModel):
    """
    End-to-end RAG pipeline metrics.

    Tracks the complete RAG workflow from query to answer.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    pipeline_name: str = Field(..., description="Name of RAG pipeline")

    # Pipeline Stage Latencies
    query_preprocessing_ms: float = Field(0.0, description="Query preprocessing time")
    embedding_generation_ms: float = Field(0.0, description="Embedding generation time")
    vector_search_ms: float = Field(0.0, description="Vector search time")
    reranking_ms: Optional[float] = Field(None, description="Reranking time")
    llm_generation_ms: float = Field(0.0, description="LLM generation time")
    postprocessing_ms: float = Field(0.0, description="Postprocessing time")
    total_pipeline_ms: float = Field(..., description="Total pipeline time")

    # Stage Success
    stages_completed: int = Field(0, description="Number of stages completed")
    stages_failed: int = Field(0, description="Number of stages failed")
    failed_stage: Optional[str] = Field(None, description="Name of failed stage if any")

    # Token Usage
    embedding_tokens: int = Field(0, description="Tokens used for embeddings")
    llm_prompt_tokens: int = Field(0, description="LLM prompt tokens")
    llm_completion_tokens: int = Field(0, description="LLM completion tokens")

    # Cost
    embedding_cost_usd: float = Field(0.0, description="Embedding cost in USD")
    llm_cost_usd: float = Field(0.0, description="LLM cost in USD")
    total_cost_usd: float = Field(0.0, description="Total cost in USD")

    # Quality
    pipeline_success: bool = Field(True, description="Did pipeline complete successfully?")
    quality_score: Optional[float] = Field(None, description="Composite quality score (0.0-1.0)", ge=0.0, le=1.0)

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When pipeline executed")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "pipeline_name": "qa_pipeline",
                "embedding_generation_ms": 15.0,
                "vector_search_ms": 45.2,
                "llm_generation_ms": 850.0,
                "total_pipeline_ms": 920.5,
                "stages_completed": 5,
                "llm_prompt_tokens": 450,
                "llm_completion_tokens": 120,
                "total_cost_usd": 0.00175,
                "pipeline_success": True,
                "quality_score": 0.89
            }
        }
