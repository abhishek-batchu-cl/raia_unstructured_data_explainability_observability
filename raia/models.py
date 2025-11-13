"""
RAIA Inspectors - Data Models

Pydantic models for capturing agent execution metrics, behavioral signals, and semantic scores.
"""

from datetime import datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class RAIAAgentRun(BaseModel):
    """
    Represents a complete agent execution run with aggregate metrics.
    """
    run_id: str = Field(..., description="Unique identifier for this run")
    session_id: Optional[str] = Field(None, description="Session ID grouping multiple runs")
    agent_name: Optional[str] = Field(None, description="Name of the agent")
    graph_name: Optional[str] = Field(None, description="Name of the LangGraph graph")
    start_time: datetime = Field(..., description="When the run started")
    end_time: Optional[datetime] = Field(None, description="When the run ended")
    status: Literal["success", "error", "in_progress"] = Field("in_progress", description="Run status")
    total_latency_ms: Optional[float] = Field(None, description="Total execution time in milliseconds")
    total_tokens_prompt: Optional[int] = Field(None, description="Total prompt tokens used")
    total_tokens_completion: Optional[int] = Field(None, description="Total completion tokens used")
    total_cost_usd: Optional[float] = Field(None, description="Estimated total cost in USD")

    # Task Success Metrics (NEW - Industry-leading)
    task_completed: Optional[bool] = Field(None, description="Whether the task was completed")
    task_completion_rate: Optional[float] = Field(None, description="Task completion rate (0.0-1.0)")
    goal_achieved: Optional[bool] = Field(None, description="Whether the goal was achieved")
    goal_achievement_score: Optional[float] = Field(None, description="Goal achievement score (0.0-1.0)")
    success_criteria: Optional[list[str]] = Field(None, description="List of success criteria to evaluate")
    criteria_met: Optional[list[str]] = Field(None, description="Which success criteria were met")

    # Streaming Metrics (NEW - For better UX tracking)
    time_to_first_token_ms: Optional[float] = Field(None, description="Time to first token in milliseconds")
    tokens_per_second: Optional[float] = Field(None, description="Streaming rate (tokens/sec)")
    streaming_enabled: Optional[bool] = Field(None, description="Whether streaming was used")

    # Error & Retry Metrics (NEW - Enhanced error tracking)
    error_count: int = Field(0, description="Total number of errors encountered")
    retry_count: int = Field(0, description="Total number of retries attempted")
    recovery_successful: Optional[bool] = Field(None, description="Whether agent recovered from errors")
    fallback_used: Optional[bool] = Field(None, description="Whether fallback logic was triggered")

    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "session_id": "session_xyz",
                "agent_name": "medical_research_agent",
                "graph_name": "react_graph",
                "start_time": "2024-01-15T10:30:00Z",
                "end_time": "2024-01-15T10:30:45Z",
                "status": "success",
                "total_latency_ms": 45000.0,
                "total_tokens_prompt": 1200,
                "total_tokens_completion": 800,
                "total_cost_usd": 0.0245,
                "metadata": {"environment": "production", "tenant": "acme"}
            }
        }


class RAIANodeMetrics(BaseModel):
    """
    Metrics for a single node/step in the agent execution.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: str = Field(..., description="Name of the node/step")
    node_type: Literal["llm", "tool", "chain", "custom"] = Field(..., description="Type of node")
    start_time: datetime = Field(..., description="When the node started")
    end_time: datetime = Field(..., description="When the node ended")
    latency_ms: float = Field(..., description="Execution time in milliseconds")
    tokens_prompt: Optional[int] = Field(None, description="Prompt tokens for this node")
    tokens_completion: Optional[int] = Field(None, description="Completion tokens for this node")
    cost_usd: Optional[float] = Field(None, description="Estimated cost for this node in USD")
    success: bool = Field(True, description="Whether the node executed successfully")
    error_type: Optional[str] = Field(None, description="Error type if failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retries attempted")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "search_pubmed",
                "node_type": "tool",
                "start_time": "2024-01-15T10:30:10Z",
                "end_time": "2024-01-15T10:30:12Z",
                "latency_ms": 2000.0,
                "success": True,
                "retry_count": 0
            }
        }


class RAIAFunctionalSignal(BaseModel):
    """
    Represents a detected behavioral pattern or issue during execution.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: Optional[str] = Field(None, description="Node where signal was detected")
    signal_type: Literal[
        "loop_detected",
        "redundant_tool_use",
        "bad_tool_choice",
        "state_inconsistency",
        "policy_violation",
        "safety_risk",
        "suboptimal_path",
        "info_redundancy"
    ] = Field(..., description="Type of behavioral signal")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level")
    message: str = Field(..., description="Human-readable description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When signal was created")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "search_node",
                "signal_type": "redundant_tool_use",
                "severity": "medium",
                "message": "Tool 'search_pubmed' called 3 times with similar queries within 5 seconds",
                "metadata": {"tool_calls": ["call_1", "call_2", "call_3"]}
            }
        }


class RAIASemanticScore(BaseModel):
    """
    Semantic quality score for agent output or behavior.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: Optional[str] = Field(None, description="Node being evaluated")
    dimension: Literal[
        "hallucination_risk",
        "instruction_adherence",
        "business_rule_compliance",
        "answer_consistency",
        "clarity",
        "tone_appropriateness"
    ] = Field(..., description="Semantic dimension being scored")
    score: float = Field(..., description="Score value (0-1 scale)", ge=0.0, le=1.0)
    explanation: Optional[str] = Field(None, description="Explanation of the score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When score was created")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "final_answer",
                "dimension": "hallucination_risk",
                "score": 0.15,
                "explanation": "Response is well-grounded in retrieved context with minimal speculation",
                "metadata": {"evaluator": "gpt-4", "confidence": 0.89}
            }
        }


# =============================================================================
# RAG EVALUATION MODELS
# =============================================================================


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


class RAIAEmbeddingDriftMetrics(BaseModel):
    """
    Metrics for detecting embedding drift over time.

    UNIQUE TO RAIA - No competitor offers comprehensive embedding drift detection!

    Monitors changes in embedding distributions to detect data drift.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    index_name: str = Field(..., description="Name of vector index/database")

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


class RAIAVectorIndexHealth(BaseModel):
    """
    Metrics for monitoring vector database/index health.

    UNIQUE TO RAIA - No competitor offers vector index health monitoring!
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
