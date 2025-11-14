#!/usr/bin/env python3
"""
Populate ALL 15 RAIA Tables with Realistic Data
================================================

This script populates the missing 10 tables in complete_end_to_end_demo.db
to make it a truly comprehensive demonstration.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from raia import (
    SQLiteRAIAStorage,
    RAIASemanticScore,
    RAIAAgentDecision,
    RAIANodeMetrics,
    RAIAPipelineMetrics,
    RAIAEmbeddingDriftMetrics,
    RAIAVectorIndexHealth,
    RAIAFunctionalSignal,
    RAIACounterfactualScenario,
    RAIASensitivityAnalysis,
    RAIAOptimizationRecommendation,
)


def populate_semantic_scores(storage, run_ids):
    """Add semantic quality scores."""
    print("\n📊 Populating semantic scores...")
    # Valid dimensions from RAIASemanticScore model
    dimensions = ["hallucination_risk", "instruction_adherence", "clarity"]

    for run_id in run_ids:
        for dim in dimensions:
            score = RAIASemanticScore(
                run_id=run_id,
                dimension=dim,
                score=random.uniform(0.7, 0.95),
                reasoning=f"Measured {dim} quality using NLP metrics"
            )
            storage.save_semantic_score(score)

    print(f"   ✅ Added {len(run_ids) * len(dimensions)} semantic scores")


def populate_agent_decisions(storage, run_ids):
    """Add agent decision points."""
    print("\n🤖 Populating agent decisions...")

    decision_points = [
        {
            "point": "retrieval_strategy",
            "options": ["semantic_search", "keyword_search", "hybrid"],
            "chosen": "semantic_search"
        },
        {
            "point": "answer_format",
            "options": ["brief", "detailed", "step_by_step"],
            "chosen": "detailed"
        },
        {
            "point": "source_selection",
            "options": ["top_1", "top_3", "top_5"],
            "chosen": "top_3"
        },
    ]

    for run_id in run_ids:
        for dp in decision_points:
            decision = RAIAAgentDecision(
                run_id=run_id,
                node_name="decision_maker",
                decision_point=dp["point"],
                selected_action=dp["chosen"],
                selection_rationale=f"Selected {dp['chosen']} based on query complexity",
                selection_confidence=random.uniform(0.75, 0.95),
                alternatives_considered=[],
                num_alternatives=0,
                context_used=dp["options"]
            )
            storage.save_agent_decision(decision)

    print(f"   ✅ Added {len(run_ids) * len(decision_points)} agent decisions")


def populate_node_metrics(storage, run_ids):
    """Add node-level execution metrics."""
    print("\n⚙️  Populating node metrics...")

    nodes = [
        {"name": "query_analyzer", "type": "llm"},
        {"name": "retriever", "type": "tool"},
        {"name": "generator", "type": "llm"},
        {"name": "validator", "type": "tool"},
    ]

    for run_id in run_ids:
        for node in nodes:
            now = datetime.utcnow()
            latency = random.uniform(10, 100)
            metrics = RAIANodeMetrics(
                run_id=run_id,
                node_name=node["name"],
                node_type=node["type"],
                start_time=now - timedelta(milliseconds=latency),
                end_time=now,
                latency_ms=latency,
                success=True,
                retry_count=0
            )
            storage.save_node_metrics(metrics)

    print(f"   ✅ Added {len(run_ids) * len(nodes)} node metrics")


def populate_pipeline_metrics(storage, run_ids):
    """Add pipeline-level metrics."""
    print("\n🔄 Populating pipeline metrics...")

    for run_id in run_ids:
        total_pipeline_ms = random.uniform(50, 200)
        metrics = RAIAPipelineMetrics(
            run_id=run_id,
            pipeline_name="rag_pipeline",
            query_preprocessing_ms=random.uniform(5, 15),
            embedding_generation_ms=random.uniform(10, 30),
            vector_search_ms=random.uniform(15, 40),
            llm_generation_ms=random.uniform(20, 100),
            postprocessing_ms=random.uniform(5, 15),
            total_pipeline_ms=total_pipeline_ms,
            stages_completed=5,
            stages_failed=0,
            pipeline_success=True,
            quality_score=random.uniform(0.8, 0.95)
        )
        storage.save_pipeline_metrics(metrics)

    print(f"   ✅ Added {len(run_ids)} pipeline metrics")


def populate_embedding_drift(storage):
    """Add embedding drift detection metrics."""
    print("\n📉 Populating embedding drift metrics...")

    # Baseline
    drift1 = RAIAEmbeddingDriftMetrics(
        index_name="knowledge_base_v1",
        kl_divergence=0.05,
        js_divergence=0.03,
        wasserstein_distance=0.08,
        drift_detected=False,
        drift_severity="low",
        samples_analyzed=6,
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    storage.save_embedding_drift_metrics(drift1)

    # After update - drift detected!
    drift2 = RAIAEmbeddingDriftMetrics(
        index_name="knowledge_base_v2",
        kl_divergence=0.25,
        js_divergence=0.18,
        wasserstein_distance=0.32,
        drift_detected=True,
        drift_severity="high",
        samples_analyzed=6,
        created_at=datetime.utcnow()
    )
    storage.save_embedding_drift_metrics(drift2)

    print(f"   ✅ Added 2 embedding drift metrics")


def populate_vector_health(storage):
    """Add vector index health metrics."""
    print("\n🏥 Populating vector index health...")

    now = datetime.utcnow()
    health = RAIAVectorIndexHealth(
        index_name="knowledge_base_v1",
        total_documents=6,
        total_embeddings=6,
        index_size_mb=2.5,
        avg_query_latency_ms=15.3,
        last_updated=now,
        staleness_hours=2.5
    )
    storage.save_vector_index_health(health)

    print(f"   ✅ Added 1 vector index health record")


def populate_functional_signals(storage, run_ids):
    """Add functional correctness signals."""
    print("\n✅ Populating functional signals...")

    signal_types = [
        "loop_detected",
        "redundant_tool_use",
        "suboptimal_path"
    ]

    for run_id in run_ids[:5]:  # First 5 runs
        for signal_type in signal_types:
            signal = RAIAFunctionalSignal(
                run_id=run_id,
                node_name="analyzer",
                signal_type=signal_type,
                severity="low",
                message=f"Signal detected: {signal_type} in execution trace"
            )
            storage.save_functional_signal(signal)

    print(f"   ✅ Added {5 * len(signal_types)} functional signals")


def populate_counterfactuals(storage, run_ids):
    """Add counterfactual scenarios for what-if analysis."""
    print("\n🔮 Populating counterfactual scenarios...")

    scenarios = [
        {
            "name": "Increase retrieval from 3 to 5 documents",
            "type": "retrieval",
            "original_quality": 0.85,
            "original_latency": 150.0,
            "original_cost": 0.001,
            "alternative_quality": 0.88,
            "alternative_latency": 200.0,
            "alternative_cost": 0.0015,
            "recommendation": "test_further"
        },
        {
            "name": "Switch to hybrid search",
            "type": "retrieval",
            "original_quality": 0.85,
            "original_latency": 150.0,
            "original_cost": 0.001,
            "alternative_quality": 0.92,
            "alternative_latency": 220.0,
            "alternative_cost": 0.0018,
            "recommendation": "adopt"
        },
        {
            "name": "Reduce chunk size to 256",
            "type": "parameter",
            "original_quality": 0.85,
            "original_latency": 150.0,
            "original_cost": 0.001,
            "alternative_quality": 0.82,
            "alternative_latency": 120.0,
            "alternative_cost": 0.0008,
            "recommendation": "reject"
        },
    ]

    for run_id in run_ids[:3]:  # First 3 runs
        for scenario in scenarios:
            quality_delta = scenario["alternative_quality"] - scenario["original_quality"]
            latency_delta = scenario["alternative_latency"] - scenario["original_latency"]
            cost_delta = scenario["alternative_cost"] - scenario["original_cost"]

            counterfactual = RAIACounterfactualScenario(
                run_id=run_id,
                scenario_name=scenario["name"],
                scenario_type=scenario["type"],
                original_config={"quality": scenario["original_quality"]},
                alternative_config={"quality": scenario["alternative_quality"]},
                original_quality=scenario["original_quality"],
                original_latency_ms=scenario["original_latency"],
                original_cost_usd=scenario["original_cost"],
                alternative_quality=scenario["alternative_quality"],
                alternative_latency_ms=scenario["alternative_latency"],
                alternative_cost_usd=scenario["alternative_cost"],
                quality_delta=quality_delta,
                quality_delta_pct=(quality_delta / scenario["original_quality"] * 100) if scenario["original_quality"] > 0 else 0,
                latency_delta_ms=latency_delta,
                latency_delta_pct=(latency_delta / scenario["original_latency"] * 100) if scenario["original_latency"] > 0 else 0,
                cost_delta_usd=cost_delta,
                cost_delta_pct=(cost_delta / scenario["original_cost"] * 100) if scenario["original_cost"] > 0 else 0,
                is_improvement=quality_delta > 0,
                recommendation=scenario["recommendation"],
                recommendation_rationale=f"Based on what-if analysis for {scenario['name']}",
                confidence=random.uniform(0.7, 0.9)
            )
            storage.save_counterfactual_scenario(counterfactual)

    print(f"   ✅ Added {3 * len(scenarios)} counterfactual scenarios")


def populate_sensitivity_analysis(storage):
    """Add sensitivity analysis results."""
    print("\n📈 Populating sensitivity analysis...")

    from raia.models_whatif import ParameterSensitivity

    analyses = [
        {
            "name": "Temperature Sensitivity Analysis",
            "params": [
                {
                    "param": "temperature",
                    "type": "float",
                    "min": 0.0,
                    "max": 1.0,
                    "samples": 5,
                    "quality_sensitivity": 0.75,
                    "latency_sensitivity": 0.2,
                    "cost_sensitivity": 0.1,
                    "optimal": 0.7,
                    "impact": "high"
                }
            ],
            "most_sensitive": "temperature",
            "least_sensitive": "temperature"
        },
        {
            "name": "Chunk Size Sensitivity Analysis",
            "params": [
                {
                    "param": "chunk_size",
                    "type": "int",
                    "min": 128,
                    "max": 1024,
                    "samples": 5,
                    "quality_sensitivity": 0.65,
                    "latency_sensitivity": 0.45,
                    "cost_sensitivity": 0.35,
                    "optimal": 512,
                    "impact": "high"
                }
            ],
            "most_sensitive": "chunk_size",
            "least_sensitive": "chunk_size"
        },
    ]

    for analysis in analyses:
        # Create ParameterSensitivity objects
        param_sensitivities = []
        for p in analysis["params"]:
            param_sens = ParameterSensitivity(
                parameter_name=p["param"],
                parameter_type=p["type"],
                min_value=p["min"],
                max_value=p["max"],
                num_samples=p["samples"],
                quality_sensitivity=p["quality_sensitivity"],
                latency_sensitivity=p["latency_sensitivity"],
                cost_sensitivity=p["cost_sensitivity"],
                optimal_value=p["optimal"],
                optimal_rationale=f"Optimal value for {p['param']}",
                impact_level=p["impact"]
            )
            param_sensitivities.append(param_sens)

        sensitivity = RAIASensitivityAnalysis(
            run_id="sensitivity_analysis_run",
            analysis_name=analysis["name"],
            parameters=param_sensitivities,
            most_sensitive_param=analysis["most_sensitive"],
            least_sensitive_param=analysis["least_sensitive"],
            optimal_config={analysis["most_sensitive"]: analysis["params"][0]["optimal"]},
            expected_improvement=0.15,
            num_simulations=100,
            analysis_duration_ms=5000.0
        )
        storage.save_sensitivity_analysis(sensitivity)

    print(f"   ✅ Added {len(analyses)} sensitivity analyses")


def populate_optimization_recommendations(storage):
    """Add optimization recommendations."""
    print("\n💡 Populating optimization recommendations...")

    recommendations = [
        {
            "name": "Implement Semantic Chunking",
            "goal": "quality",
            "current_quality": 0.82,
            "current_latency": 150.0,
            "current_cost": 0.001,
            "expected_quality": 0.91,
            "expected_latency": 160.0,
            "expected_cost": 0.0011,
            "difficulty": "medium",
            "risk": "low",
            "priority": "high"
        },
        {
            "name": "Enable Hybrid Search",
            "goal": "quality",
            "current_quality": 0.78,
            "current_latency": 150.0,
            "current_cost": 0.001,
            "expected_quality": 0.87,
            "expected_latency": 200.0,
            "expected_cost": 0.0015,
            "difficulty": "easy",
            "risk": "low",
            "priority": "high"
        },
        {
            "name": "Implement Chain-of-Thought",
            "goal": "quality",
            "current_quality": 0.75,
            "current_latency": 150.0,
            "current_cost": 0.001,
            "expected_quality": 0.88,
            "expected_latency": 250.0,
            "expected_cost": 0.002,
            "difficulty": "hard",
            "risk": "medium",
            "priority": "medium"
        },
    ]

    for rec in recommendations:
        quality_improvement = rec["expected_quality"] - rec["current_quality"]
        latency_change = rec["expected_latency"] - rec["current_latency"]
        cost_change = rec["expected_cost"] - rec["current_cost"]

        recommendation = RAIAOptimizationRecommendation(
            run_id="optimization_run",
            recommendation_name=rec["name"],
            optimization_goal=rec["goal"],
            current_quality=rec["current_quality"],
            current_latency_ms=rec["current_latency"],
            current_cost_usd=rec["current_cost"],
            expected_quality=rec["expected_quality"],
            expected_latency_ms=rec["expected_latency"],
            expected_cost_usd=rec["expected_cost"],
            recommended_changes={
                "strategy": rec["name"].lower().replace(" ", "_")
            },
            quality_improvement_pct=(quality_improvement / rec["current_quality"] * 100) if rec["current_quality"] > 0 else 0,
            latency_improvement_pct=(-latency_change / rec["current_latency"] * 100) if rec["current_latency"] > 0 else 0,
            cost_savings_pct=(-cost_change / rec["current_cost"] * 100) if rec["current_cost"] > 0 else 0,
            implementation_difficulty=rec["difficulty"],
            implementation_steps=[
                f"Step 1 for {rec['name']}",
                f"Step 2 for {rec['name']}"
            ],
            estimated_implementation_time="1-2 weeks",
            risk_level=rec["risk"],
            risks=[f"Potential risk for {rec['name']}"],
            mitigation_strategies=[f"Mitigation for {rec['name']}"],
            priority=rec["priority"],
            priority_rationale=f"{rec['name']} is a {rec['priority']} priority optimization"
        )
        storage.save_optimization_recommendation(recommendation)

    print(f"   ✅ Added {len(recommendations)} optimization recommendations")


def main():
    print("="*80)
    print("  POPULATING ALL 15 RAIA TABLES")
    print("  Database: complete_end_to_end_demo.db")
    print("="*80)

    # Initialize storage
    storage = SQLiteRAIAStorage("complete_end_to_end_demo.db")

    # Get existing run IDs from database
    import sqlite3
    conn = sqlite3.connect("complete_end_to_end_demo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT run_id FROM raia_retrieval_metrics")
    run_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"\nFound {len(run_ids)} existing runs to enhance")

    # Populate all missing tables
    populate_semantic_scores(storage, run_ids)
    populate_agent_decisions(storage, run_ids)
    populate_node_metrics(storage, run_ids)
    populate_pipeline_metrics(storage, run_ids)
    populate_embedding_drift(storage)
    populate_vector_health(storage)
    populate_functional_signals(storage, run_ids)
    populate_counterfactuals(storage, run_ids)
    populate_sensitivity_analysis(storage)
    populate_optimization_recommendations(storage)

    # Verify all tables
    print("\n" + "="*80)
    print("  VERIFICATION: Checking all tables")
    print("="*80)

    conn = sqlite3.connect("complete_end_to_end_demo.db")
    cursor = conn.cursor()

    tables = [
        "raia_retrieval_metrics",
        "raia_answer_quality_metrics",
        "raia_attribution_maps",
        "raia_reasoning_traces",
        "raia_semantic_scores",
        "raia_agent_decisions",
        "raia_node_metrics",
        "raia_pipeline_metrics",
        "raia_embedding_drift_metrics",
        "raia_vector_index_health",
        "raia_functional_signals",
        "raia_counterfactual_scenarios",
        "raia_sensitivity_analyses",
        "raia_optimization_recommendations",
    ]

    populated_count = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {table:<45} {count:>5} rows")
            if count > 0:
                populated_count += 1
        except Exception as e:
            print(f"  ❌ {table:<45} ERROR")

    conn.close()

    print("\n" + "="*80)
    print(f"  ✅ COMPLETE: {populated_count}/14 tables populated")
    print(f"  Database: complete_end_to_end_demo.db")
    print("="*80)
    print()


if __name__ == "__main__":
    import json
    main()
