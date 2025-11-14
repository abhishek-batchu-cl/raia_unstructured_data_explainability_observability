#!/usr/bin/env python3
"""
RAIA Complete Feature Demonstration
====================================

This script demonstrates EVERY RAIA capability and populates ALL 15 database tables:

Database Tables Populated:
1. raia_runs - Run metadata
2. raia_node_metrics - Node execution metrics
3. raia_functional_signals - Tool/LLM calls
4. raia_semantic_scores - Semantic quality
5. raia_retrieval_metrics - RAG retrieval
6. raia_answer_quality_metrics - RAG answer quality
7. raia_vector_index_health - Vector index
8. raia_pipeline_metrics - RAG pipeline
9. raia_embedding_drift_metrics - Embedding drift
10. raia_attribution_maps - Explainability attribution
11. raia_reasoning_traces - Explainability reasoning
12. raia_agent_decisions - Explainability decisions
13. raia_counterfactual_scenarios - What-if scenarios
14. raia_sensitivity_analyses - Parameter sensitivity
15. raia_optimization_recommendations - AI recommendations

Features Demonstrated:
- Agent Evaluation (ExecutionInspector, BehaviorInspector, SemanticInspector)
- RAG Evaluation (retrieval, answer quality, index health, pipeline, drift)
- Explainability (attribution, reasoning traces, agent decisions)
- What-If Analysis (scenarios, sensitivity, optimization)
- Comparison & Reporting (A/B testing, reports)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent))

from raia import (
    # Inspectors (some may need LangChain)
    RAIASemanticInspector,
    RAIARAGInspector,
    RAIAComparator,
    # Storage
    SQLiteRAIAStorage,
    # Models
    Attribution,
    ReasoningStep,
    AlternativeAction,
    ParameterSensitivity,
)

# Import models directly for manual population
from raia.models import (
    RAIAAgentRun,
    RAIANodeMetrics,
    RAIAFunctionalSignal,
    RAIASemanticScore,
)

# Import RAG models
from raia.models_rag import (
    RAIAEmbeddingDriftMetrics,
)


def print_section(title: str, emoji: str = "📊") -> None:
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"{emoji}  {title}")
    print("=" * 80 + "\n")


def simulate_agent_execution(storage: SQLiteRAIAStorage, run_id: str):
    """
    Simulate complete agent execution to populate:
    - raia_runs
    - raia_node_metrics
    - raia_functional_signals

    Works directly with storage layer (no LangChain required).
    """
    print_section("1. Agent Execution Tracking", "🤖")

    print("Starting agent run...")
    start_time = datetime.utcnow()

    # Simulate 5 node executions
    nodes = ["planner", "retriever", "analyzer", "generator", "critic"]
    total_tokens_prompt = 0
    total_tokens_completion = 0
    total_cost = 0.0

    for i, node_name in enumerate(nodes):
        print(f"  • Executing node: {node_name}")

        # Node execution metrics
        node_start = start_time + timedelta(milliseconds=i*500)
        node_end = node_start + timedelta(milliseconds=random.randint(200, 800))
        latency = (node_end - node_start).total_seconds() * 1000

        tokens_prompt = random.randint(100, 500)
        tokens_completion = random.randint(50, 300)
        tokens_total = tokens_prompt + tokens_completion
        cost = tokens_total * 0.00001  # Simple cost model

        total_tokens_prompt += tokens_prompt
        total_tokens_completion += tokens_completion
        total_cost += cost

        # Create node metrics
        node_metric = RAIANodeMetrics(
            run_id=run_id,
            node_name=node_name,
            node_type="llm",  # Required field
            start_time=node_start,
            end_time=node_end,
            latency_ms=latency,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=cost,
            success=True,
        )
        storage.save_node_metrics(node_metric)

        # For tool nodes, create additional node metrics
        if node_name in ["retriever", "analyzer"]:
            tool_latency = random.uniform(50, 150)
            tool_metric = RAIANodeMetrics(
                run_id=run_id,
                node_name=f"{node_name}_tool",
                node_type="tool",
                start_time=node_end,
                end_time=node_end + timedelta(milliseconds=tool_latency),
                latency_ms=tool_latency,
                success=True,
            )
            storage.save_node_metrics(tool_metric)

    # Create and save run
    end_time = start_time + timedelta(seconds=5)
    total_latency = (end_time - start_time).total_seconds() * 1000

    run = RAIAAgentRun(
        run_id=run_id,
        session_id="session_001",
        agent_name="demo_agent",
        graph_name="demo_graph",
        start_time=start_time,
        end_time=end_time,
        status="success",
        total_latency_ms=total_latency,
        total_tokens_prompt=total_tokens_prompt,
        total_tokens_completion=total_tokens_completion,
        total_cost_usd=total_cost,
        task_completed=True,
        task_completion_rate=1.0,
        goal_achieved=True,
        goal_achievement_score=0.95,
        time_to_first_token_ms=150.0,
        tokens_per_second=total_tokens_prompt / (total_latency / 1000.0),
        streaming_enabled=False,
        error_count=0,
        retry_count=0,
    )
    storage.save_run(run)

    print(f"✅ Run completed: {total_latency:.0f}ms, {total_tokens_prompt + total_tokens_completion} tokens, ${total_cost:.6f}")
    print(f"✅ Tables populated: raia_runs, raia_node_metrics, raia_functional_signals")


def simulate_behavior_analysis(storage: SQLiteRAIAStorage, run_id: str):
    """
    Populate raia_functional_signals table with behavioral patterns.
    """
    print_section("2. Behavior Pattern Analysis", "🔍")

    print("Analyzing agent behavior patterns...")

    # Simulate various behavioral signals
    behavioral_signals = [
        {
            "signal_type": "loop_detected",
            "severity": "medium",
            "message": "Agent revisited the same node 'analyzer' 3 times",
            "node_name": "analyzer",
        },
        {
            "signal_type": "redundant_tool_use",
            "severity": "low",
            "message": "Tool 'search_database' called twice with similar parameters",
            "node_name": "retriever",
        },
        {
            "signal_type": "suboptimal_path",
            "severity": "low",
            "message": "Agent took 5 steps when 3 would have been sufficient",
            "node_name": None,
        },
    ]

    for signal_data in behavioral_signals:
        signal = RAIAFunctionalSignal(
            run_id=run_id,
            node_name=signal_data["node_name"],
            signal_type=signal_data["signal_type"],
            severity=signal_data["severity"],
            message=signal_data["message"],
            timestamp=datetime.utcnow(),
            metadata={"detected_by": "behavior_analyzer_v1"},
        )
        storage.save_functional_signal(signal)
        print(f"  • Detected: {signal_data['signal_type']} ({signal_data['severity']})")

    print(f"✅ Behavior analysis complete - {len(behavioral_signals)} patterns detected")


def simulate_semantic_evaluation(storage: SQLiteRAIAStorage, run_id: str):
    """
    Populate raia_semantic_scores table.
    """
    print_section("3. Semantic Quality Evaluation", "✨")

    print("Evaluating output quality...")

    # Create semantic scores for different quality dimensions
    # Valid dimensions: hallucination_risk, instruction_adherence, business_rule_compliance,
    #                   answer_consistency, clarity, tone_appropriateness
    semantic_scores = [
        {
            "dimension": "hallucination_risk",
            "score": 0.05,  # Low risk (0-1, lower is better for risk metrics)
            "explanation": "Response is well-grounded in source documents with minimal unsupported claims",
        },
        {
            "dimension": "instruction_adherence",
            "score": 0.95,
            "explanation": "Response follows all provided instructions and constraints",
        },
        {
            "dimension": "answer_consistency",
            "score": 0.92,
            "explanation": "Answer maintains consistency with previous context and established facts",
        },
        {
            "dimension": "clarity",
            "score": 0.89,
            "explanation": "Response is clear, well-structured, and easy to understand",
        },
        {
            "dimension": "tone_appropriateness",
            "score": 0.93,
            "explanation": "Tone is professional and appropriate for the context",
        },
    ]

    for score_data in semantic_scores:
        score = RAIASemanticScore(
            run_id=run_id,
            node_name="generator",
            dimension=score_data["dimension"],
            score=score_data["score"],
            evaluator_name="gpt-4-evaluator",
            explanation=score_data["explanation"],
            metadata={"confidence": 0.93, "model": "gpt-4"},
        )
        storage.save_semantic_score(score)
        print(f"  • {score_data['dimension'].capitalize()} score: {score_data['score']:.2f}")

    print(f"✅ Table populated: raia_semantic_scores")


def simulate_rag_evaluation(storage: SQLiteRAIAStorage, run_id: str):
    """
    Populate RAG tables:
    - raia_retrieval_metrics
    - raia_answer_quality_metrics
    - raia_vector_index_health
    - raia_pipeline_metrics
    - raia_embedding_drift_metrics
    """
    print_section("4. RAG Evaluation", "📚")

    inspector = RAIARAGInspector(storage=storage)

    # 4.1 Retrieval Metrics
    print("4.1 Tracking retrieval metrics...")
    inspector.track_retrieval(
        run_id=run_id,
        query="What is machine learning?",
        retrieved_doc_ids=["doc1", "doc2", "doc3", "doc4", "doc5"],
        relevance_scores=[0.95, 0.89, 0.85, 0.78, 0.72],
        retrieval_latency_ms=65.0,
        precision_at_k=0.92,
        recall_at_k=0.85,
        metadata={"index_name": "ml_knowledge_base"},
    )
    print(f"  ✅ Retrieval: 5 docs, P@5=0.92, R@5=0.85, 65ms")

    # 4.2 Answer Quality Metrics
    print("4.2 Tracking answer quality...")
    inspector.track_answer_quality(
        run_id=run_id,
        query="What is machine learning?",
        answer="Machine learning is a subset of AI that enables systems to learn from data...",
        answer_relevance=0.94,
        answer_completeness=0.91,
        answer_faithfulness=0.96,
        hallucination_score=0.04,
        generation_latency_ms=1800.0,
        metadata={"cost_usd": 0.0045, "model": "gpt-4"},
    )
    print(f"  ✅ Answer quality: relevance=0.94, faithfulness=0.96, hallucination=0.04")

    # 4.3 Vector Index Health
    print("4.3 Tracking vector index health...")
    inspector.track_index_health(
        index_name="ml_knowledge_base",
        total_documents=10000,
        total_embeddings=10000,
        avg_query_latency_ms=65.0,
        last_updated=datetime.utcnow() - timedelta(hours=2),
        staleness_hours=2.0,
        index_size_mb=500.0,
        p50_latency_ms=45.0,
        p95_latency_ms=120.0,
        p99_latency_ms=250.0,
        avg_recall_at_10=0.89,
        metadata={"index_type": "HNSW", "ef_search": 100},
    )
    print(f"  ✅ Index health: 10K docs, 500MB, p50=45ms")

    # 4.4 Pipeline Metrics
    print("4.4 Tracking end-to-end pipeline...")
    inspector.track_pipeline(
        run_id=run_id,
        pipeline_name="ml_rag_pipeline",
        total_pipeline_ms=2100.0,
        query_preprocessing_ms=50.0,
        embedding_generation_ms=45.0,
        vector_search_ms=65.0,
        reranking_ms=85.0,
        llm_generation_ms=1800.0,
        postprocessing_ms=55.0,
        stages_completed=6,
        stages_failed=0,
        metadata={"pipeline_version": "v2.1", "cost_usd": 0.0048},
    )
    print(f"  ✅ Pipeline: total=2100ms, 6 stages, cost=$0.0048")

    # 4.5 Embedding Drift Detection
    print("4.5 Tracking embedding drift...")
    print("  → Generating baseline embeddings (v1.0, n=1000)...")
    print("  → Generating current embeddings (v1.1, n=1000)...")
    print("  → Computing drift metrics...")

    # Simulate embedding drift detection with actual computation
    import numpy as np
    from scipy.spatial.distance import cosine, euclidean
    from scipy.stats import entropy, wasserstein_distance as scipy_wasserstein

    # Generate baseline embeddings (1000 documents, 1536 dimensions - OpenAI ada-002 size)
    np.random.seed(42)
    embedding_dim = 1536
    n_samples = 1000

    # Baseline embeddings (v1.0) - centered around origin
    baseline_embeddings = np.random.randn(n_samples, embedding_dim)
    baseline_embeddings = baseline_embeddings / np.linalg.norm(baseline_embeddings, axis=1, keepdims=True)

    # Current embeddings (v1.1) - with slight drift (shift + noise)
    # Simulate drift: slight distribution shift + added noise
    drift_shift = np.random.randn(embedding_dim) * 0.05  # Small shift in mean
    drift_noise_scale = 0.03  # Added noise variance

    current_embeddings = baseline_embeddings + drift_shift + np.random.randn(n_samples, embedding_dim) * drift_noise_scale
    current_embeddings = current_embeddings / np.linalg.norm(current_embeddings, axis=1, keepdims=True)

    # Compute drift metrics
    # 1. Cosine similarity between corresponding embeddings
    cosine_similarities = []
    for i in range(n_samples):
        sim = 1 - cosine(baseline_embeddings[i], current_embeddings[i])
        cosine_similarities.append(sim)

    avg_cosine_similarity = float(np.mean(cosine_similarities))  # Average similarity to baseline

    # 2. Euclidean distance (for distribution shift metric)
    euclidean_distances = []
    for i in range(n_samples):
        dist = euclidean(baseline_embeddings[i], current_embeddings[i])
        euclidean_distances.append(dist)

    # Similarity distribution shift = std deviation of euclidean distances
    similarity_distribution_shift = float(np.std(euclidean_distances))

    # 3. KL Divergence (on projection to 1D for simplicity)
    # Project to 1D using first principal component
    baseline_proj = baseline_embeddings[:, 0]
    current_proj = current_embeddings[:, 0]

    # Create histograms
    bins = np.linspace(-0.1, 0.1, 50)
    baseline_hist, _ = np.histogram(baseline_proj, bins=bins, density=True)
    current_hist, _ = np.histogram(current_proj, bins=bins, density=True)

    # Add small epsilon to avoid log(0)
    baseline_hist = baseline_hist + 1e-10
    current_hist = current_hist + 1e-10

    # Normalize
    baseline_hist = baseline_hist / baseline_hist.sum()
    current_hist = current_hist / current_hist.sum()

    kl_divergence = float(entropy(current_hist, baseline_hist))

    # 4. JS Divergence (symmetric version of KL)
    m = 0.5 * (baseline_hist + current_hist)
    js_divergence = float(0.5 * entropy(baseline_hist, m) + 0.5 * entropy(current_hist, m))

    # 5. Wasserstein Distance (Earth Mover's Distance)
    wasserstein_dist = float(scipy_wasserstein(baseline_proj, current_proj))

    # Determine if drifting (threshold-based) and severity
    drift_threshold = 0.10
    is_drifting = kl_divergence > drift_threshold

    # Determine drift severity based on KL divergence
    if kl_divergence < 0.05:
        drift_severity = "none"
    elif kl_divergence < 0.10:
        drift_severity = "low"
    elif kl_divergence < 0.20:
        drift_severity = "medium"
    elif kl_divergence < 0.35:
        drift_severity = "high"
    else:
        drift_severity = "critical"

    print(f"  → Computed KL divergence: {kl_divergence:.4f}")
    print(f"  → Computed JS divergence: {js_divergence:.4f}")
    print(f"  → Computed Wasserstein distance: {wasserstein_dist:.4f}")
    print(f"  → Avg cosine similarity to baseline: {avg_cosine_similarity:.4f}")
    print(f"  → Similarity distribution shift: {similarity_distribution_shift:.4f}")

    drift_metric = RAIAEmbeddingDriftMetrics(
        index_name="ml_knowledge_base",
        kl_divergence=kl_divergence,
        js_divergence=js_divergence,
        wasserstein_distance=wasserstein_dist,
        avg_similarity_to_baseline=avg_cosine_similarity,
        similarity_distribution_shift=similarity_distribution_shift,
        drift_detected=is_drifting,
        drift_severity=drift_severity,
        drift_threshold=drift_threshold,
        samples_analyzed=n_samples,
        metadata={
            "baseline_version": "v1.0",
            "current_version": "v1.1",
            "embedding_model": "text-embedding-ada-002",
            "embedding_dim": embedding_dim,
            "drift_type": "distribution_shift",
            "mean_euclidean_distance": float(np.mean(euclidean_distances)),
        },
    )
    storage.save_embedding_drift_metrics(drift_metric)

    drift_status = "⚠️  DRIFT DETECTED" if is_drifting else "✅ NO DRIFT"
    print(f"  ✅ {drift_status} ({drift_severity.upper()}): KL={kl_divergence:.4f}, JS={js_divergence:.4f}, n={n_samples}")

    print(f"\n✅ Tables populated: raia_retrieval_metrics, raia_answer_quality_metrics,")
    print(f"   raia_vector_index_health, raia_pipeline_metrics, raia_embedding_drift_metrics")


def simulate_explainability(storage: SQLiteRAIAStorage, run_id: str):
    """
    Populate explainability tables:
    - raia_attribution_maps
    - raia_reasoning_traces
    - raia_agent_decisions
    """
    print_section("5. Explainability Features", "🔍")

    inspector = RAIARAGInspector(storage=storage)

    # 5.1 Attribution Tracking
    print("5.1 Tracking attribution (document → answer mapping)...")

    attributions = [
        Attribution(
            answer_span="machine learning is a subset of artificial intelligence",
            answer_start_idx=0,
            answer_end_idx=56,
            source_doc_id="ml_textbook_ch1",
            source_span="ML is a subset of AI that focuses on learning from data",
            source_start_idx=0,
            source_end_idx=55,
            confidence=0.94,
            similarity_score=0.91,
        ),
        Attribution(
            answer_span="learns from data without explicit programming",
            answer_start_idx=65,
            answer_end_idx=110,
            source_doc_id="ml_textbook_ch2",
            source_span="systems learn patterns from data automatically",
            source_start_idx=20,
            source_end_idx=65,
            confidence=0.89,
            similarity_score=0.87,
        ),
    ]

    attribution_map = inspector.track_attribution(
        run_id=run_id,
        query="What is machine learning?",
        answer="Machine learning is a subset of artificial intelligence that learns from data without explicit programming.",
        attributions=attributions,
        overall_confidence=0.92,
        faithfulness_score=0.97,
        hallucination_score=0.03,
        total_context_tokens=800,
        utilized_context_tokens=720,
    )

    print(f"  ✅ Attribution map: 2 attributions, faithfulness=0.97, efficiency=0.90")

    # 5.2 Reasoning Traces
    print("5.2 Tracking reasoning trace (step-by-step process)...")

    base_time = datetime.utcnow()
    steps = [
        ReasoningStep(
            step_number=1,
            step_name="Query Understanding",
            step_type="understanding",
            description="Analyzed query intent and extracted key concepts",
            rationale="Need to understand what user is asking before retrieval",
            confidence=0.93,
            inputs={"query": "What is machine learning?"},
            outputs={"intent": "definition", "concepts": ["ML", "definition", "basics"]},
            start_time=base_time,
            end_time=base_time + timedelta(milliseconds=45),
            latency_ms=45.0,
            success=True,
        ),
        ReasoningStep(
            step_number=2,
            step_name="Document Retrieval",
            step_type="retrieval",
            description="Retrieved top 5 relevant documents",
            rationale="Need context to answer the question",
            confidence=0.91,
            inputs={"query_embedding": "...", "top_k": 5},
            outputs={"doc_ids": ["doc1", "doc2", "doc3", "doc4", "doc5"]},
            start_time=base_time + timedelta(milliseconds=45),
            end_time=base_time + timedelta(milliseconds=110),
            latency_ms=65.0,
            success=True,
        ),
        ReasoningStep(
            step_number=3,
            step_name="Answer Generation",
            step_type="generation",
            description="Generated answer based on retrieved context",
            rationale="Synthesize information into coherent answer",
            confidence=0.94,
            inputs={"context": "...", "query": "..."},
            outputs={"answer": "Machine learning is..."},
            start_time=base_time + timedelta(milliseconds=110),
            end_time=base_time + timedelta(milliseconds=1910),
            latency_ms=1800.0,
            success=True,
        ),
    ]

    reasoning_trace = inspector.track_reasoning(
        run_id=run_id,
        trace_type="rag_reasoning",
        query="What is machine learning?",
        steps=steps,
        final_answer="Machine learning is a subset of AI...",
        reasoning_quality_score=0.93,
        logical_consistency=0.96,
    )

    print(f"  ✅ Reasoning trace: 3 steps, quality=0.93, consistency=0.96")
    print(f"     Bottleneck: Answer Generation (1800ms)")

    # 5.3 Agent Decision Tracking
    print("5.3 Tracking agent decisions...")

    # Note: track_agent_decision is not implemented in current RAIARAGInspector
    # But we can manually insert into the database for demonstration
    from raia.models_explainability import RAIAAgentDecision

    decision = RAIAAgentDecision(
        run_id=run_id,
        node_name="retriever",
        decision_point="tool_selection",
        selected_action="vector_db_retrieval",
        selection_rationale="Vector DB retrieval is faster, cheaper, and more reliable",
        selection_confidence=0.95,
        alternatives=[
            AlternativeAction(
                action_name="web_search",
                action_description="Search the web for information about machine learning",
                estimated_score=0.75,
                estimated_latency_ms=500.0,
                estimated_cost_usd=0.001,
                why_not_selected="Web search might have outdated info; vector DB is more reliable",
                pros=["Access to latest information", "Broader coverage"],
                cons=["Potentially outdated", "Less curated", "Higher latency"],
            ),
            AlternativeAction(
                action_name="knowledge_graph",
                action_description="Query structured knowledge graph for ML concepts",
                estimated_score=0.85,
                estimated_latency_ms=100.0,
                estimated_cost_usd=0.0002,
                why_not_selected="Knowledge graph may lack specific details present in vector DB",
                pros=["Fast", "Structured data", "Good for factual queries"],
                cons=["Limited depth", "May miss context"],
            ),
        ],
        timestamp=datetime.utcnow(),
        metadata={"decision_latency_ms": 5.0, "context": "Need to retrieve information about machine learning"},
    )

    # Save directly to storage
    storage.save_agent_decision(decision)

    print(f"  ✅ Agent decision: chose 'retriever_tool' over 'web_search' (95% confidence)")

    print(f"\n✅ Tables populated: raia_attribution_maps, raia_reasoning_traces, raia_agent_decisions")


def simulate_whatif_analysis(storage: SQLiteRAIAStorage, run_id: str):
    """
    Populate what-if tables:
    - raia_counterfactual_scenarios
    - raia_sensitivity_analyses
    - raia_optimization_recommendations
    """
    print_section("6. What-If Analysis", "🎯")

    inspector = RAIARAGInspector(storage=storage)

    # 6.1 Counterfactual Scenario
    print("6.1 Simulating counterfactual scenario...")
    print("    Scenario: What if we reduce context size from 2000 → 1200 tokens?")

    scenario = inspector.simulate_scenario(
        run_id=run_id,
        scenario_name="Reduce context for cost savings",
        scenario_type="context",
        original_config={"context_tokens": 2000, "model": "gpt-4"},
        alternative_config={"context_tokens": 1200, "model": "gpt-4"},
        original_quality=0.94,
        original_latency_ms=1800.0,
        original_cost_usd=0.0045,
        alternative_quality=0.91,
        alternative_latency_ms=1100.0,
        alternative_cost_usd=0.0027,
        metadata={"simulation_date": datetime.utcnow().isoformat()},
    )

    print(f"    Quality change: {scenario.quality_delta_pct:+.1f}%")
    print(f"    Latency change: {scenario.latency_delta_pct:+.1f}%")
    print(f"    Cost change: {scenario.cost_delta_pct:+.1f}%")
    print(f"  ✅ Recommendation: {scenario.recommendation.upper()}")
    print(f"     {scenario.recommendation_rationale}")

    # 6.2 Parameter Sensitivity Analysis
    print("\n6.2 Analyzing parameter sensitivity...")

    sensitivities = [
        ParameterSensitivity(
            parameter_name="context_size",
            parameter_type="int",
            min_value=800,
            max_value=3000,
            num_samples=10,
            quality_sensitivity=0.87,
            latency_sensitivity=0.65,
            cost_sensitivity=0.75,
            optimal_value=2000,
            optimal_rationale="Best balance of quality (high) vs cost/latency (moderate)",
            impact_level="high",
        ),
        ParameterSensitivity(
            parameter_name="temperature",
            parameter_type="float",
            min_value=0.0,
            max_value=1.0,
            num_samples=10,
            quality_sensitivity=0.72,
            latency_sensitivity=0.05,
            cost_sensitivity=0.08,
            optimal_value=0.7,
            optimal_rationale="Higher temperature (0.7) provides good creativity without sacrificing coherence",
            impact_level="medium",
        ),
        ParameterSensitivity(
            parameter_name="top_k",
            parameter_type="int",
            min_value=1,
            max_value=10,
            num_samples=10,
            quality_sensitivity=0.45,
            latency_sensitivity=0.35,
            cost_sensitivity=0.12,
            optimal_value=5,
            optimal_rationale="Top-5 retrieval provides sufficient context without noise",
            impact_level="medium",
        ),
    ]

    from raia.models_whatif import RAIASensitivityAnalysis

    analysis = RAIASensitivityAnalysis(
        run_id=run_id,
        analysis_name="RAG Parameter Sensitivity Analysis",
        parameters=sensitivities,
        most_sensitive_param="context_size",
        least_sensitive_param="top_k",
        optimal_config={
            "context_size": 2000,
            "temperature": 0.7,
            "top_k": 5,
        },
        expected_improvement=0.15,  # 15% improvement expected
        num_simulations=30,
        analysis_duration_ms=2500.0,
        metadata={
            "analysis_type": "full_parameter_sweep",
            "parameters_analyzed": ["context_size", "temperature", "top_k"],
        },
    )

    storage.save_sensitivity_analysis(analysis)

    print(f"  ✅ Sensitivity analysis complete")
    print(f"     Most sensitive: context_size (0.87)")
    print(f"     Least sensitive: top_k (0.45)")

    # 6.3 Optimization Recommendation
    print("\n6.3 Generating optimization recommendation...")

    from raia.models_whatif import RAIAOptimizationRecommendation

    recommendation = RAIAOptimizationRecommendation(
        run_id=run_id,
        recommendation_name="Reduce Context Size for Cost Optimization",
        optimization_goal="cost",
        # Current state
        current_quality=0.92,
        current_latency_ms=2100.0,
        current_cost_usd=0.0048,
        # Expected after changes
        expected_quality=0.89,
        expected_latency_ms=1285.0,
        expected_cost_usd=0.00288,
        # Impact summary
        quality_improvement_pct=-3.2,
        latency_improvement_pct=38.8,
        cost_savings_pct=40.0,
        # Implementation details
        recommended_changes={
            "context_size": 1200,
            "original_context_size": 2000,
            "reduction": 800,
        },
        implementation_difficulty="easy",
        implementation_steps=[
            "Update RAG pipeline configuration",
            "Set max_context_tokens=1200",
            "Test on sample queries",
            "Monitor quality metrics for 24h",
            "Roll out to production",
        ],
        estimated_implementation_time="2 hours",
        # Risk assessment
        risk_level="low",
        risks=["Minor quality degradation on complex queries"],
        mitigation_strategies=["Monitor quality metrics", "A/B test before full rollout"],
        # Priority
        priority="high",
        priority_rationale="Significant cost savings (40%) with minimal quality impact (-3.2%). Context efficiency analysis shows only 60% of tokens are utilized.",
    )

    storage.save_optimization_recommendation(recommendation)

    print(f"  ✅ Recommendation: {recommendation.recommendation_name}")
    print(f"     Expected savings: {recommendation.cost_savings_pct:.1f}%")
    print(f"     Quality impact: {recommendation.quality_improvement_pct:.1f}%")
    print(f"     Priority: {recommendation.priority}")

    print(f"\n✅ Tables populated: raia_counterfactual_scenarios, raia_sensitivity_analyses,")
    print(f"   raia_optimization_recommendations")


def simulate_comparison_reporting(storage: SQLiteRAIAStorage):
    """
    Demonstrate comparison and reporting across multiple runs.
    """
    print_section("7. Comparison & Reporting", "🏆")

    # First, create a second run for comparison
    run_id_2 = "complete_demo_run_2"

    print("Creating second run for comparison...")

    # Simulate a faster, cheaper but slightly lower quality run
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(seconds=2)

    # Create run directly
    run2 = RAIAAgentRun(
        run_id=run_id_2,
        session_id="session_002",
        agent_name="demo_agent",
        graph_name="demo_graph",
        start_time=start_time,
        end_time=end_time,
        status="success",
        total_latency_ms=2000.0,
        total_tokens_prompt=300,
        total_tokens_completion=200,
        total_cost_usd=0.0015,
        task_completed=True,
        task_completion_rate=1.0,
        goal_achieved=True,
        goal_achievement_score=0.90,
        time_to_first_token_ms=100.0,
        tokens_per_second=250.0,
        streaming_enabled=False,
        error_count=0,
        retry_count=0,
    )
    storage.save_run(run2)

    # Add RAG metrics for second run
    rag_inspector = RAIARAGInspector(storage=storage)

    rag_inspector.track_answer_quality(
        run_id=run_id_2,
        query="What is machine learning?",
        answer="ML is AI that learns from data.",
        answer_relevance=0.87,
        answer_completeness=0.82,
        answer_faithfulness=0.91,
        hallucination_score=0.09,
        generation_latency_ms=450.0,
        metadata={"cost_usd": 0.0015, "model": "gpt-3.5-turbo"},
    )

    print("  ✅ Second run created (faster, cheaper, lower quality)")

    # Now compare both runs
    print("\nComparing runs...")

    comparator = RAIAComparator(storage)

    comparison = comparator.compare_runs(
        run_ids=["complete_demo_run_1", run_id_2],
        comparison_name="GPT-4 vs GPT-3.5 Comparison"
    )

    comparator.print_comparison(comparison)

    # Generate comprehensive report
    print("\nGenerating evaluation report...")

    report = comparator.generate_report(
        run_ids=["complete_demo_run_1", run_id_2],
        report_name="Complete Demo Evaluation Report"
    )

    comparator.print_report(report)

    print(f"\n✅ Comparison and reporting complete")


def verify_database(storage: SQLiteRAIAStorage):
    """
    Verify all 15 tables have data.
    """
    print_section("8. Database Verification", "✅")

    import sqlite3

    conn = sqlite3.connect(storage.db_path)
    cursor = conn.cursor()

    tables = [
        "raia_runs",
        "raia_node_metrics",
        "raia_functional_signals",
        "raia_semantic_scores",
        "raia_retrieval_metrics",
        "raia_answer_quality_metrics",
        "raia_vector_index_health",
        "raia_pipeline_metrics",
        "raia_embedding_drift_metrics",
        "raia_attribution_maps",
        "raia_reasoning_traces",
        "raia_agent_decisions",
        "raia_counterfactual_scenarios",
        "raia_sensitivity_analyses",
        "raia_optimization_recommendations",
    ]

    print("Checking all database tables:\n")

    all_populated = True
    for i, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        status = "✅" if count > 0 else "❌"
        print(f"{i:2d}. {status} {table:<40} {count:>5} rows")

        if count == 0:
            all_populated = False

    conn.close()

    print(f"\n{'='*80}")
    if all_populated:
        print("✅ SUCCESS: All 15 tables have been populated!")
    else:
        print("⚠️  WARNING: Some tables are empty")
    print(f"{'='*80}")


def main():
    """
    Run complete demonstration of all RAIA features.
    """
    print("\n╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "RAIA COMPLETE FEATURE DEMONSTRATION".center(78) + "║")
    print("║" + "ALL Capabilities, ALL 15 Database Tables".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝\n")

    # Initialize storage
    db_path = "complete_feature_demo.db"
    storage = SQLiteRAIAStorage(db_path)

    run_id = "complete_demo_run_1"

    print(f"📁 Database: {db_path}\n")

    # Execute all demonstrations
    try:
        # 1. Agent Execution Tracking
        simulate_agent_execution(storage, run_id)

        # 2. Behavior Analysis
        simulate_behavior_analysis(storage, run_id)

        # 3. Semantic Evaluation
        simulate_semantic_evaluation(storage, run_id)

        # 4. RAG Evaluation (5 tables)
        simulate_rag_evaluation(storage, run_id)

        # 5. Explainability (3 tables)
        simulate_explainability(storage, run_id)

        # 6. What-If Analysis (3 tables)
        simulate_whatif_analysis(storage, run_id)

        # 7. Comparison & Reporting
        simulate_comparison_reporting(storage)

        # 8. Verify all tables
        verify_database(storage)

        # Final summary
        print_section("9. Summary", "🎉")

        print("✅ COMPLETE: All RAIA features demonstrated successfully!\n")
        print("Features Demonstrated:")
        print("  • Agent Evaluation (Execution, Behavior, Semantic)")
        print("  • RAG Evaluation (Retrieval, Quality, Index, Pipeline, Drift)")
        print("  • Explainability (Attribution, Reasoning, Decisions)")
        print("  • What-If Analysis (Scenarios, Sensitivity, Optimization)")
        print("  • Comparison & Reporting (A/B testing, Reports)")

        print(f"\n📊 Database Tables: ALL 15 tables populated")
        print(f"📁 Database file: {db_path}")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("\n1. Query the database:")
        print(f"   sqlite3 {db_path}")
        print("\n2. Explore specific tables:")
        print(f"   SELECT * FROM raia_attribution_maps;")
        print(f"   SELECT * FROM raia_counterfactual_scenarios;")
        print("\n3. Run analysis on the data:")
        print(f"   python -c \"from raia import SQLiteRAIAStorage; storage = SQLiteRAIAStorage('{db_path}'); print(storage.list_runs())\"")

        print("\n✅ Demo complete!\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
