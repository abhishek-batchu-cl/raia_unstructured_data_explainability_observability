"""
RAIA RAG Evaluation Inspector

Specialized inspector for evaluating RAG (Retrieval-Augmented Generation) systems,
including retrieval quality, answer faithfulness, embedding drift detection,
and vector index health monitoring.

UNIQUE TO RAIA - No competitor offers comprehensive RAG evaluation with drift detection!
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
import logging

from raia.models import (
    RAIARetrievalMetrics,
    RAIAAnswerQualityMetrics,
    RAIAEmbeddingDriftMetrics,
    RAIAVectorIndexHealth,
    RAIAPipelineMetrics,
)
from raia.models_explainability import (
    Attribution,
    RAIAAttributionMap,
    ReasoningStep,
    RAIAReasoningTrace,
    AlternativeAction,
    RAIAAgentDecision,
)
from raia.models_whatif import (
    RAIACounterfactualScenario,
    ParameterSensitivity,
    RAIASensitivityAnalysis,
    RAIAOptimizationRecommendation,
)
from raia.storage.base import BaseRAIAStorage


logger = logging.getLogger(__name__)


class RAIARAGInspector:
    """
    Inspector for RAG (Retrieval-Augmented Generation) evaluation.

    Provides comprehensive RAG evaluation including:
    - Retrieval quality metrics (precision, recall, MRR, NDCG)
    - Answer quality and faithfulness
    - Embedding drift detection (UNIQUE to RAIA!)
    - Vector index health monitoring (UNIQUE to RAIA!)
    - End-to-end pipeline tracking

    Example:
        ```python
        from raia.inspectors.rag import RAIARAGInspector
        from raia.storage.sqlite import SQLiteRAIAStorage

        storage = SQLiteRAIAStorage()
        inspector = RAIARAGInspector(storage=storage)

        # Track retrieval
        inspector.track_retrieval(
            run_id="run_123",
            query="What is the capital of France?",
            retrieved_docs=["doc1", "doc2", "doc3"],
            relevance_scores=[0.95, 0.87, 0.65],
            latency_ms=45.2
        )

        # Track answer quality
        inspector.track_answer_quality(
            run_id="run_123",
            query="What is the capital of France?",
            answer="The capital of France is Paris.",
            faithfulness=0.95,
            hallucination_score=0.05
        )

        # Check for embedding drift
        drift = inspector.check_embedding_drift(
            index_name="my_index",
            current_embeddings=new_embeddings,
            baseline_embeddings=baseline_embeddings
        )
        ```
    """

    def __init__(
        self,
        storage: Optional[BaseRAIAStorage] = None,
        drift_threshold: float = 0.05,
    ):
        """
        Initialize RAG inspector.

        Args:
            storage: Storage backend for metrics (optional)
            drift_threshold: Threshold for detecting embedding drift (default: 0.05)
        """
        self.storage = storage
        self.drift_threshold = drift_threshold
        logger.info(f"Initialized RAIA RAG Inspector (drift_threshold={drift_threshold})")

    def track_retrieval(
        self,
        run_id: str,
        query: str,
        retrieved_doc_ids: List[str],
        relevance_scores: Optional[List[float]] = None,
        retrieval_latency_ms: float = 0.0,
        rerank_latency_ms: Optional[float] = None,
        # Quality metrics
        precision_at_k: Optional[float] = None,
        recall_at_k: Optional[float] = None,
        mrr: Optional[float] = None,
        ndcg: Optional[float] = None,
        context_relevance_score: Optional[float] = None,
        context_diversity: Optional[float] = None,
        context_coverage: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIARetrievalMetrics:
        """
        Track retrieval metrics for a RAG query.

        Args:
            run_id: Run identifier
            query: User query
            retrieved_doc_ids: List of retrieved document IDs
            relevance_scores: Relevance scores for each document (optional)
            retrieval_latency_ms: Retrieval latency in milliseconds
            rerank_latency_ms: Reranking latency in milliseconds (optional)
            precision_at_k: Precision@K metric
            recall_at_k: Recall@K metric
            mrr: Mean Reciprocal Rank
            ndcg: Normalized Discounted Cumulative Gain
            context_relevance_score: Average relevance of retrieved docs
            context_diversity: Diversity of retrieved docs
            context_coverage: How well results cover query topic
            metadata: Additional metadata

        Returns:
            RAIARetrievalMetrics object
        """
        total_latency_ms = retrieval_latency_ms + (rerank_latency_ms or 0.0)

        metrics = RAIARetrievalMetrics(
            run_id=run_id,
            query=query,
            retrieved_count=len(retrieved_doc_ids),
            precision_at_k=precision_at_k,
            recall_at_k=recall_at_k,
            mrr=mrr,
            ndcg=ndcg,
            retrieval_latency_ms=retrieval_latency_ms,
            rerank_latency_ms=rerank_latency_ms,
            total_latency_ms=total_latency_ms,
            context_relevance_score=context_relevance_score,
            context_diversity=context_diversity,
            context_coverage=context_coverage,
            retrieved_doc_ids=retrieved_doc_ids,
            relevance_scores=relevance_scores or [],
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_retrieval_metrics(metrics)
            logger.debug(f"Saved retrieval metrics for run {run_id}")

        return metrics

    def track_answer_quality(
        self,
        run_id: str,
        query: str,
        answer: str,
        # Faithfulness metrics
        answer_faithfulness: Optional[float] = None,
        hallucination_score: Optional[float] = None,
        citation_accuracy: Optional[float] = None,
        # Quality metrics
        answer_relevance: Optional[float] = None,
        answer_completeness: Optional[float] = None,
        answer_conciseness: Optional[float] = None,
        # Context utilization
        context_utilization: Optional[float] = None,
        context_recall: Optional[float] = None,
        # Contradiction detection
        self_contradiction: Optional[bool] = None,
        context_contradiction: Optional[bool] = None,
        generation_latency_ms: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAAnswerQualityMetrics:
        """
        Track answer quality metrics for a RAG response.

        Args:
            run_id: Run identifier
            query: User query
            answer: Generated answer
            answer_faithfulness: Is answer grounded in context? (0.0-1.0)
            hallucination_score: Hallucination score (0=none, 1=full)
            citation_accuracy: Accuracy of citations/sources
            answer_relevance: Does answer address query?
            answer_completeness: Is answer complete?
            answer_conciseness: Is answer concise?
            context_utilization: How much context was used?
            context_recall: Did answer use all relevant context?
            self_contradiction: Does answer contradict itself?
            context_contradiction: Does answer contradict context?
            generation_latency_ms: Answer generation latency
            metadata: Additional metadata

        Returns:
            RAIAAnswerQualityMetrics object
        """
        metrics = RAIAAnswerQualityMetrics(
            run_id=run_id,
            query=query,
            answer=answer,
            answer_faithfulness=answer_faithfulness,
            hallucination_score=hallucination_score,
            citation_accuracy=citation_accuracy,
            answer_relevance=answer_relevance,
            answer_completeness=answer_completeness,
            answer_conciseness=answer_conciseness,
            context_utilization=context_utilization,
            context_recall=context_recall,
            self_contradiction=self_contradiction,
            context_contradiction=context_contradiction,
            generation_latency_ms=generation_latency_ms,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_answer_quality_metrics(metrics)
            logger.debug(f"Saved answer quality metrics for run {run_id}")

        return metrics

    def check_embedding_drift(
        self,
        index_name: str,
        kl_divergence: Optional[float] = None,
        js_divergence: Optional[float] = None,
        wasserstein_distance: Optional[float] = None,
        avg_similarity_to_baseline: Optional[float] = None,
        similarity_distribution_shift: Optional[float] = None,
        baseline_period_start: Optional[datetime] = None,
        baseline_period_end: Optional[datetime] = None,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        samples_analyzed: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAEmbeddingDriftMetrics:
        """
        Check for embedding drift in vector database.

        UNIQUE TO RAIA - No competitor offers comprehensive embedding drift detection!

        This method detects changes in embedding distributions over time,
        which can indicate data drift that degrades RAG system performance.

        Args:
            index_name: Name of vector index/database
            kl_divergence: KL divergence from baseline
            js_divergence: Jensen-Shannon divergence (0.0-1.0)
            wasserstein_distance: Earth mover's distance
            avg_similarity_to_baseline: Average cosine similarity to baseline
            similarity_distribution_shift: Change in similarity distribution
            baseline_period_start: Start of baseline period
            baseline_period_end: End of baseline period
            current_period_start: Start of current period
            current_period_end: End of current period
            samples_analyzed: Number of samples analyzed
            metadata: Additional metadata

        Returns:
            RAIAEmbeddingDriftMetrics object with drift status
        """
        # Determine drift status based on available metrics
        drift_detected = False
        drift_severity: Literal["none", "low", "medium", "high", "critical"] = "none"

        # Check KL divergence (primary metric)
        if kl_divergence is not None:
            if kl_divergence > self.drift_threshold:
                drift_detected = True
                if kl_divergence < self.drift_threshold * 2:
                    drift_severity = "low"
                elif kl_divergence < self.drift_threshold * 5:
                    drift_severity = "medium"
                elif kl_divergence < self.drift_threshold * 10:
                    drift_severity = "high"
                else:
                    drift_severity = "critical"

        # Check JS divergence (secondary metric)
        elif js_divergence is not None:
            if js_divergence > self.drift_threshold:
                drift_detected = True
                if js_divergence < self.drift_threshold * 2:
                    drift_severity = "low"
                elif js_divergence < self.drift_threshold * 5:
                    drift_severity = "medium"
                elif js_divergence < self.drift_threshold * 10:
                    drift_severity = "high"
                else:
                    drift_severity = "critical"

        metrics = RAIAEmbeddingDriftMetrics(
            index_name=index_name,
            kl_divergence=kl_divergence,
            js_divergence=js_divergence,
            wasserstein_distance=wasserstein_distance,
            avg_similarity_to_baseline=avg_similarity_to_baseline,
            similarity_distribution_shift=similarity_distribution_shift,
            drift_detected=drift_detected,
            drift_severity=drift_severity,
            drift_threshold=self.drift_threshold,
            baseline_period_start=baseline_period_start,
            baseline_period_end=baseline_period_end,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            samples_analyzed=samples_analyzed,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_embedding_drift_metrics(metrics)
            logger.info(
                f"Saved drift metrics for {index_name}: "
                f"drift_detected={drift_detected}, severity={drift_severity}"
            )

        return metrics

    def track_index_health(
        self,
        index_name: str,
        total_documents: int,
        total_embeddings: int,
        avg_query_latency_ms: float,
        last_updated: datetime,
        staleness_hours: float,
        # Optional metrics
        index_size_mb: Optional[float] = None,
        p50_latency_ms: Optional[float] = None,
        p95_latency_ms: Optional[float] = None,
        p99_latency_ms: Optional[float] = None,
        avg_recall_at_10: Optional[float] = None,
        recall_degradation_pct: Optional[float] = None,
        pending_updates: int = 0,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_pct: Optional[float] = None,
        disk_usage_mb: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAVectorIndexHealth:
        """
        Track vector index health metrics.

        UNIQUE TO RAIA - No competitor offers vector index health monitoring!

        Args:
            index_name: Name of vector index/database
            total_documents: Total documents in index
            total_embeddings: Total embeddings in index
            avg_query_latency_ms: Average query latency
            last_updated: When index was last updated
            staleness_hours: Hours since last update
            index_size_mb: Index size in megabytes
            p50_latency_ms: 50th percentile latency
            p95_latency_ms: 95th percentile latency
            p99_latency_ms: 99th percentile latency
            avg_recall_at_10: Average recall@10
            recall_degradation_pct: Percentage change in recall
            pending_updates: Documents waiting to be indexed
            memory_usage_mb: Memory usage in megabytes
            cpu_usage_pct: CPU usage percentage
            disk_usage_mb: Disk usage in megabytes
            metadata: Additional metadata

        Returns:
            RAIAVectorIndexHealth object with health status
        """
        # Determine health status
        health_status: Literal["healthy", "degraded", "critical"] = "healthy"
        health_issues: List[str] = []

        # Check latency
        if p95_latency_ms and p95_latency_ms > 500:
            health_status = "degraded"
            health_issues.append(f"High P95 latency: {p95_latency_ms}ms")
        elif avg_query_latency_ms > 1000:
            health_status = "critical"
            health_issues.append(f"Critical latency: {avg_query_latency_ms}ms")

        # Check recall degradation
        if recall_degradation_pct:
            if recall_degradation_pct > 20:
                health_status = "critical"
                health_issues.append(f"Severe recall degradation: {recall_degradation_pct}%")
            elif recall_degradation_pct > 10:
                if health_status == "healthy":
                    health_status = "degraded"
                health_issues.append(f"Recall degradation: {recall_degradation_pct}%")

        # Check staleness
        if staleness_hours > 48:
            if health_status == "healthy":
                health_status = "degraded"
            health_issues.append(f"Index stale: {staleness_hours} hours since update")

        # Check pending updates
        if pending_updates > total_documents * 0.1:  # > 10% backlog
            if health_status == "healthy":
                health_status = "degraded"
            health_issues.append(f"Large update backlog: {pending_updates} pending")

        metrics = RAIAVectorIndexHealth(
            index_name=index_name,
            total_documents=total_documents,
            total_embeddings=total_embeddings,
            index_size_mb=index_size_mb,
            avg_query_latency_ms=avg_query_latency_ms,
            p50_latency_ms=p50_latency_ms,
            p95_latency_ms=p95_latency_ms,
            p99_latency_ms=p99_latency_ms,
            avg_recall_at_10=avg_recall_at_10,
            recall_degradation_pct=recall_degradation_pct,
            last_updated=last_updated,
            staleness_hours=staleness_hours,
            pending_updates=pending_updates,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_pct=cpu_usage_pct,
            disk_usage_mb=disk_usage_mb,
            health_status=health_status,
            health_issues=health_issues,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_vector_index_health(metrics)
            logger.info(
                f"Saved index health for {index_name}: status={health_status}, "
                f"issues={len(health_issues)}"
            )

        return metrics

    def track_pipeline(
        self,
        run_id: str,
        pipeline_name: str,
        total_pipeline_ms: float,
        # Stage latencies
        query_preprocessing_ms: float = 0.0,
        embedding_generation_ms: float = 0.0,
        vector_search_ms: float = 0.0,
        reranking_ms: Optional[float] = None,
        llm_generation_ms: float = 0.0,
        postprocessing_ms: float = 0.0,
        # Stage completion
        stages_completed: int = 0,
        stages_failed: int = 0,
        failed_stage: Optional[str] = None,
        # Token usage
        embedding_tokens: int = 0,
        llm_prompt_tokens: int = 0,
        llm_completion_tokens: int = 0,
        # Costs
        embedding_cost_usd: float = 0.0,
        llm_cost_usd: float = 0.0,
        total_cost_usd: float = 0.0,
        # Quality
        pipeline_success: bool = True,
        quality_score: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAPipelineMetrics:
        """
        Track end-to-end RAG pipeline metrics.

        Args:
            run_id: Run identifier
            pipeline_name: Name of RAG pipeline
            total_pipeline_ms: Total pipeline latency
            query_preprocessing_ms: Query preprocessing time
            embedding_generation_ms: Embedding generation time
            vector_search_ms: Vector search time
            reranking_ms: Reranking time (optional)
            llm_generation_ms: LLM generation time
            postprocessing_ms: Postprocessing time
            stages_completed: Number of stages completed
            stages_failed: Number of stages failed
            failed_stage: Name of failed stage if any
            embedding_tokens: Tokens used for embeddings
            llm_prompt_tokens: LLM prompt tokens
            llm_completion_tokens: LLM completion tokens
            embedding_cost_usd: Embedding cost in USD
            llm_cost_usd: LLM cost in USD
            total_cost_usd: Total cost in USD
            pipeline_success: Did pipeline complete successfully?
            quality_score: Composite quality score (0.0-1.0)
            metadata: Additional metadata

        Returns:
            RAIAPipelineMetrics object
        """
        metrics = RAIAPipelineMetrics(
            run_id=run_id,
            pipeline_name=pipeline_name,
            query_preprocessing_ms=query_preprocessing_ms,
            embedding_generation_ms=embedding_generation_ms,
            vector_search_ms=vector_search_ms,
            reranking_ms=reranking_ms,
            llm_generation_ms=llm_generation_ms,
            postprocessing_ms=postprocessing_ms,
            total_pipeline_ms=total_pipeline_ms,
            stages_completed=stages_completed,
            stages_failed=stages_failed,
            failed_stage=failed_stage,
            embedding_tokens=embedding_tokens,
            llm_prompt_tokens=llm_prompt_tokens,
            llm_completion_tokens=llm_completion_tokens,
            embedding_cost_usd=embedding_cost_usd,
            llm_cost_usd=llm_cost_usd,
            total_cost_usd=total_cost_usd,
            pipeline_success=pipeline_success,
            quality_score=quality_score,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_pipeline_metrics(metrics)
            logger.debug(f"Saved pipeline metrics for run {run_id}")

        return metrics

    def track_attribution(
        self,
        run_id: str,
        query: str,
        answer: str,
        attributions: List[Attribution],
        overall_confidence: float,
        faithfulness_score: float,
        hallucination_score: float,
        total_context_tokens: int,
        utilized_context_tokens: int,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAAttributionMap:
        """
        Track attribution mapping for answer explainability.

        Shows which parts of the answer came from which source documents.
        Like SHAP for RAG: document "importance" for each answer span.

        Args:
            run_id: Unique identifier for the run
            query: User query
            answer: Generated answer
            attributions: List of attribution mappings (answer span → source doc)
            overall_confidence: Overall confidence in attribution (0-1)
            faithfulness_score: How faithful answer is to sources (0-1)
            hallucination_score: Hallucination score (0=none, 1=full)
            total_context_tokens: Total tokens in retrieved context
            utilized_context_tokens: Tokens actually used in answer
            metadata: Additional metadata

        Returns:
            RAIAAttributionMap object

        Example:
            ```python
            attributions = [
                Attribution(
                    answer_span="greenhouse gas emissions",
                    answer_start_idx=45,
                    answer_end_idx=69,
                    source_doc_id="doc_climate_science",
                    source_span="GHG emissions from fossil fuels",
                    source_start_idx=120,
                    source_end_idx=151,
                    confidence=0.95,
                    similarity_score=0.92
                )
            ]

            attribution_map = inspector.track_attribution(
                run_id="run_001",
                query="What causes climate change?",
                answer="Climate change is caused by greenhouse gas emissions...",
                attributions=attributions,
                overall_confidence=0.92,
                faithfulness_score=0.96,
                hallucination_score=0.04,
                total_context_tokens=2500,
                utilized_context_tokens=1850
            )
            ```
        """
        # Calculate derived metrics
        context_efficiency = utilized_context_tokens / total_context_tokens if total_context_tokens > 0 else 0.0
        unique_sources = len(set(attr.source_doc_id for attr in attributions))

        # Determine primary source (most attributed)
        source_counts: dict[str, int] = {}
        for attr in attributions:
            source_counts[attr.source_doc_id] = source_counts.get(attr.source_doc_id, 0) + 1
        primary_source = max(source_counts, key=source_counts.get) if source_counts else None

        attribution_map = RAIAAttributionMap(
            run_id=run_id,
            query=query,
            answer=answer,
            attributions=attributions,
            overall_confidence=overall_confidence,
            faithfulness_score=faithfulness_score,
            hallucination_score=hallucination_score,
            total_context_tokens=total_context_tokens,
            utilized_context_tokens=utilized_context_tokens,
            context_efficiency=context_efficiency,
            unique_sources_used=unique_sources,
            primary_source=primary_source,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_attribution_map(attribution_map)
            logger.debug(f"Saved attribution map for run {run_id}")

        return attribution_map

    def track_reasoning(
        self,
        run_id: str,
        trace_type: Literal["rag_reasoning", "agent_reasoning", "hybrid"],
        query: str,
        steps: List[ReasoningStep],
        final_answer: Optional[str] = None,
        reasoning_quality_score: Optional[float] = None,
        logical_consistency: Optional[float] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> RAIAReasoningTrace:
        """
        Track reasoning trace for process explainability.

        Captures step-by-step reasoning chain showing how system reasoned
        from query to answer. Like LIME for agents: local reasoning process.

        Args:
            run_id: Unique identifier for the run
            trace_type: Type of reasoning ("rag_reasoning", "agent_reasoning", "hybrid")
            query: Original user query
            steps: List of reasoning steps in order
            final_answer: Final answer/output (if available)
            reasoning_quality_score: Overall reasoning quality (0-1)
            logical_consistency: Logical consistency score (0-1)
            metadata: Additional metadata

        Returns:
            RAIAReasoningTrace object

        Example:
            ```python
            steps = [
                ReasoningStep(
                    step_number=1,
                    step_name="Query Understanding",
                    step_type="understanding",
                    description="Analyzed user query to extract intent",
                    action_taken="extract_intent(query)",
                    rationale="Need to understand query intent before retrieval",
                    confidence=0.92,
                    inputs={"query": "What causes climate change?"},
                    outputs={"intent": "causal_inquiry"},
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    latency_ms=50.0,
                    success=True
                ),
                # ... more steps
            ]

            trace = inspector.track_reasoning(
                run_id="run_001",
                trace_type="rag_reasoning",
                query="What causes climate change?",
                steps=steps,
                final_answer="Climate change is caused by...",
                reasoning_quality_score=0.89,
                logical_consistency=0.94
            )
            ```
        """
        # Calculate aggregate metrics
        total_steps = len(steps)
        successful_steps = sum(1 for step in steps if step.success)
        failed_steps = sum(1 for step in steps if not step.success)

        # Calculate total latency
        total_latency_ms = sum(step.latency_ms for step in steps)

        # Find bottleneck (slowest step)
        bottleneck_step = max(steps, key=lambda s: s.latency_ms).step_name if steps else None

        # Default quality scores if not provided
        if reasoning_quality_score is None:
            # Simple heuristic: average of step confidences
            reasoning_quality_score = sum(step.confidence for step in steps) / len(steps) if steps else 0.0

        if logical_consistency is None:
            # Simple heuristic: success rate
            logical_consistency = successful_steps / total_steps if total_steps > 0 else 1.0

        reasoning_trace = RAIAReasoningTrace(
            run_id=run_id,
            trace_type=trace_type,
            query=query,
            final_answer=final_answer,
            steps=steps,
            total_steps=total_steps,
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            reasoning_quality_score=reasoning_quality_score,
            logical_consistency=logical_consistency,
            total_latency_ms=total_latency_ms,
            bottleneck_step=bottleneck_step,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_reasoning_trace(reasoning_trace)
            logger.debug(f"Saved reasoning trace for run {run_id}")

        return reasoning_trace

    def get_retrieval_metrics(self, run_id: str) -> List[RAIARetrievalMetrics]:
        """Get all retrieval metrics for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_retrieval_metrics_for_run(run_id)

    def get_answer_quality(self, run_id: str) -> List[RAIAAnswerQualityMetrics]:
        """Get all answer quality metrics for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_answer_quality_for_run(run_id)

    def get_drift_history(self, index_name: str, limit: Optional[int] = None) -> List[RAIAEmbeddingDriftMetrics]:
        """Get embedding drift history for an index."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_embedding_drift_metrics(index_name, limit=limit)

    def get_index_health_history(self, index_name: str, limit: Optional[int] = None) -> List[RAIAVectorIndexHealth]:
        """Get index health history."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_vector_index_health(index_name, limit=limit)

    def get_pipeline_metrics(self, run_id: str) -> List[RAIAPipelineMetrics]:
        """Get all pipeline metrics for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_pipeline_metrics_for_run(run_id)

    def get_attribution_maps(self, run_id: str) -> List[RAIAAttributionMap]:
        """Get all attribution maps for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_attribution_maps_for_run(run_id)

    def get_reasoning_traces(self, run_id: str) -> List[RAIAReasoningTrace]:
        """Get all reasoning traces for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_reasoning_traces_for_run(run_id)

    def get_agent_decisions(self, run_id: str) -> List[RAIAAgentDecision]:
        """Get all agent decisions for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_agent_decisions_for_run(run_id)

    # What-If Analysis Methods

    def simulate_scenario(
        self,
        run_id: str,
        scenario_name: str,
        scenario_type: Literal["retrieval", "context", "tool_selection", "agent_path", "parameter", "drift_simulation", "cost_optimization", "quality_optimization"],
        original_config: Dict[str, Any],
        alternative_config: Dict[str, Any],
        original_quality: float,
        original_latency_ms: float,
        original_cost_usd: float,
        alternative_quality: float,
        alternative_latency_ms: float,
        alternative_cost_usd: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RAIACounterfactualScenario:
        """
        Simulate a what-if scenario and analyze the impact.

        Args:
            run_id: Parent run ID
            scenario_name: Human-readable scenario name
            scenario_type: Type of scenario (retrieval, context, etc.)
            original_config: Original configuration
            alternative_config: Alternative configuration to test
            original_quality: Original quality score
            original_latency_ms: Original latency
            original_cost_usd: Original cost
            alternative_quality: Alternative quality score
            alternative_latency_ms: Alternative latency
            alternative_cost_usd: Alternative cost
            metadata: Additional metadata

        Returns:
            RAIACounterfactualScenario with analysis and recommendation
        """
        # Calculate deltas
        quality_delta = alternative_quality - original_quality
        quality_delta_pct = (quality_delta / original_quality * 100) if original_quality > 0 else 0

        latency_delta_ms = alternative_latency_ms - original_latency_ms
        latency_delta_pct = (latency_delta_ms / original_latency_ms * 100) if original_latency_ms > 0 else 0

        cost_delta_usd = alternative_cost_usd - original_cost_usd
        cost_delta_pct = (cost_delta_usd / original_cost_usd * 100) if original_cost_usd > 0 else 0

        # Determine if improvement (simple heuristic: quality up, cost down)
        is_improvement = (quality_delta >= 0 and cost_delta_usd <= 0) or (quality_delta > 0.05 and cost_delta_pct < 20)

        # Generate recommendation
        if is_improvement:
            recommendation = "adopt"
            rationale = f"Quality improvement (+{quality_delta_pct:.1f}%) justifies cost increase (+{cost_delta_pct:.1f}%)"
            confidence = 0.85
        elif quality_delta_pct < -5:
            recommendation = "reject"
            rationale = f"Quality degradation ({quality_delta_pct:.1f}%) is too significant"
            confidence = 0.90
        elif cost_delta_pct > 50:
            recommendation = "reject"
            rationale = f"Cost increase (+{cost_delta_pct:.1f}%) is too high for minimal quality gain"
            confidence = 0.88
        else:
            recommendation = "test_further"
            rationale = "Trade-offs require more testing to determine value"
            confidence = 0.70

        # Generate pros and cons
        pros = []
        cons = []

        if quality_delta > 0:
            pros.append(f"Quality improvement: +{quality_delta_pct:.1f}%")
        else:
            cons.append(f"Quality degradation: {quality_delta_pct:.1f}%")

        if latency_delta_ms < 0:
            pros.append(f"Faster response: {latency_delta_pct:.1f}%")
        elif latency_delta_ms > 0:
            cons.append(f"Slower response: +{latency_delta_pct:.1f}%")

        if cost_delta_usd < 0:
            pros.append(f"Cost savings: {cost_delta_pct:.1f}%")
        elif cost_delta_usd > 0:
            cons.append(f"Higher cost: +{cost_delta_pct:.1f}%")

        scenario = RAIACounterfactualScenario(
            run_id=run_id,
            scenario_name=scenario_name,
            scenario_type=scenario_type,
            original_config=original_config,
            alternative_config=alternative_config,
            original_quality=original_quality,
            original_latency_ms=original_latency_ms,
            original_cost_usd=original_cost_usd,
            original_metadata=metadata,
            alternative_quality=alternative_quality,
            alternative_latency_ms=alternative_latency_ms,
            alternative_cost_usd=alternative_cost_usd,
            alternative_metadata=metadata,
            quality_delta=quality_delta,
            quality_delta_pct=quality_delta_pct,
            latency_delta_ms=latency_delta_ms,
            latency_delta_pct=latency_delta_pct,
            cost_delta_usd=cost_delta_usd,
            cost_delta_pct=cost_delta_pct,
            is_improvement=is_improvement,
            recommendation=recommendation,
            recommendation_rationale=rationale,
            confidence=confidence,
            pros=pros,
            cons=cons,
            metadata=metadata,
        )

        if self.storage:
            self.storage.save_counterfactual_scenario(scenario)
            logger.debug(f"Saved counterfactual scenario for run {run_id}")

        return scenario

    def get_counterfactual_scenarios(self, run_id: str) -> List[RAIACounterfactualScenario]:
        """Get all counterfactual scenarios for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_counterfactual_scenarios_for_run(run_id)

    def get_sensitivity_analyses(self, run_id: str) -> List[RAIASensitivityAnalysis]:
        """Get all sensitivity analyses for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_sensitivity_analyses_for_run(run_id)

    def get_optimization_recommendations(self, run_id: str) -> List[RAIAOptimizationRecommendation]:
        """Get all optimization recommendations for a run."""
        if not self.storage:
            logger.warning("No storage backend configured")
            return []
        return self.storage.get_optimization_recommendations_for_run(run_id)
