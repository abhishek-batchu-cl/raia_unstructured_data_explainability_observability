#!/usr/bin/env python3
"""
Populate missing data for drift detection and what-if analysis.
This script adds sample data to make the UI features visible.
"""

import sqlite3
import json
from datetime import datetime, timedelta
import uuid

DB_PATH = "complete_end_to_end_demo.db"

def populate_drift_metrics(conn):
    """Add sample drift detection metrics."""
    print("🔄 Populating drift detection metrics...")

    cursor = conn.cursor()

    # Generate dates for realistic timeline
    base_date = datetime(2024, 11, 1)

    # Sample drift scenarios
    drift_scenarios = [
        {
            "index_name": "knowledge_base_main",
            "kl_divergence": 0.156,
            "js_divergence": 0.089,
            "wasserstein_distance": 0.234,
            "avg_similarity_to_baseline": 0.818,
            "similarity_distribution_shift": 0.182,
            "drift_detected": True,
            "drift_severity": "moderate",
            "drift_threshold": 0.1,
            "baseline_period_start": (base_date - timedelta(days=30)).isoformat(),
            "baseline_period_end": base_date.isoformat(),
            "current_period_start": base_date.isoformat(),
            "current_period_end": (base_date + timedelta(days=7)).isoformat(),
            "samples_analyzed": 5,
            "metadata": json.dumps({"version": "v2.0", "update_type": "content_refresh"})
        },
        {
            "index_name": "knowledge_base_main",
            "kl_divergence": 0.034,
            "js_divergence": 0.019,
            "wasserstein_distance": 0.067,
            "avg_similarity_to_baseline": 0.949,
            "similarity_distribution_shift": 0.051,
            "drift_detected": False,
            "drift_severity": "low",
            "drift_threshold": 0.1,
            "baseline_period_start": (base_date - timedelta(days=60)).isoformat(),
            "baseline_period_end": (base_date - timedelta(days=30)).isoformat(),
            "current_period_start": (base_date - timedelta(days=30)).isoformat(),
            "current_period_end": base_date.isoformat(),
            "samples_analyzed": 5,
            "metadata": json.dumps({"version": "v1.5", "update_type": "minor_update"})
        },
        {
            "index_name": "knowledge_base_v3",
            "kl_divergence": 0.267,
            "js_divergence": 0.145,
            "wasserstein_distance": 0.389,
            "avg_similarity_to_baseline": 0.702,
            "similarity_distribution_shift": 0.298,
            "drift_detected": True,
            "drift_severity": "high",
            "drift_threshold": 0.1,
            "baseline_period_start": (base_date - timedelta(days=14)).isoformat(),
            "baseline_period_end": (base_date - timedelta(days=7)).isoformat(),
            "current_period_start": (base_date - timedelta(days=7)).isoformat(),
            "current_period_end": base_date.isoformat(),
            "samples_analyzed": 5,
            "metadata": json.dumps({"version": "v3.0", "update_type": "major_update"})
        },
        {
            "index_name": "knowledge_base_v2",
            "kl_divergence": 0.108,
            "js_divergence": 0.062,
            "wasserstein_distance": 0.156,
            "avg_similarity_to_baseline": 0.877,
            "similarity_distribution_shift": 0.123,
            "drift_detected": True,
            "drift_severity": "moderate",
            "drift_threshold": 0.1,
            "baseline_period_start": (base_date - timedelta(days=21)).isoformat(),
            "baseline_period_end": (base_date - timedelta(days=14)).isoformat(),
            "current_period_start": (base_date - timedelta(days=14)).isoformat(),
            "current_period_end": (base_date - timedelta(days=7)).isoformat(),
            "samples_analyzed": 5,
            "metadata": json.dumps({"version": "v2.1", "update_type": "content_update"})
        },
        {
            "index_name": "knowledge_base_v2",
            "kl_divergence": 0.063,
            "js_divergence": 0.035,
            "wasserstein_distance": 0.091,
            "avg_similarity_to_baseline": 0.922,
            "similarity_distribution_shift": 0.078,
            "drift_detected": False,
            "drift_severity": "low",
            "drift_threshold": 0.1,
            "baseline_period_start": (base_date - timedelta(days=28)).isoformat(),
            "baseline_period_end": (base_date - timedelta(days=21)).isoformat(),
            "current_period_start": (base_date - timedelta(days=21)).isoformat(),
            "current_period_end": (base_date - timedelta(days=14)).isoformat(),
            "samples_analyzed": 5,
            "metadata": json.dumps({"version": "v2.0", "update_type": "patch"})
        },
    ]

    for scenario in drift_scenarios:
        cursor.execute("""
            INSERT INTO raia_embedding_drift_metrics (
                index_name, kl_divergence, js_divergence, wasserstein_distance,
                avg_similarity_to_baseline, similarity_distribution_shift,
                drift_detected, drift_severity, drift_threshold,
                baseline_period_start, baseline_period_end,
                current_period_start, current_period_end,
                samples_analyzed, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scenario["index_name"],
            scenario["kl_divergence"],
            scenario["js_divergence"],
            scenario["wasserstein_distance"],
            scenario["avg_similarity_to_baseline"],
            scenario["similarity_distribution_shift"],
            scenario["drift_detected"],
            scenario["drift_severity"],
            scenario["drift_threshold"],
            scenario["baseline_period_start"],
            scenario["baseline_period_end"],
            scenario["current_period_start"],
            scenario["current_period_end"],
            scenario["samples_analyzed"],
            datetime.now().isoformat(),
            scenario["metadata"]
        ))

    conn.commit()
    print(f"✅ Added {len(drift_scenarios)} drift detection metrics")


def populate_whatif_data(conn):
    """Add sample what-if analysis data."""
    print("\n🔄 Populating what-if analysis data...")

    cursor = conn.cursor()

    # Counterfactual scenarios
    counterfactuals = [
        {
            "run_id": f"whatif_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Increased Chunk Size",
            "modification_type": "chunk_size",
            "parameter_changed": "chunk_size",
            "original_value": "512",
            "counterfactual_value": "1024",
            "original_score": 0.78,
            "counterfactual_score": 0.85,
            "score_difference": 0.07,
            "metric_name": "retrieval_precision"
        },
        {
            "run_id": f"whatif_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Lower Temperature",
            "modification_type": "model_parameter",
            "parameter_changed": "temperature",
            "original_value": "0.7",
            "counterfactual_value": "0.3",
            "original_score": 0.72,
            "counterfactual_score": 0.81,
            "score_difference": 0.09,
            "metric_name": "answer_relevance"
        },
        {
            "run_id": f"whatif_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "More Retrieved Docs",
            "modification_type": "retrieval_config",
            "parameter_changed": "top_k",
            "original_value": "3",
            "counterfactual_value": "5",
            "original_score": 0.75,
            "counterfactual_score": 0.79,
            "score_difference": 0.04,
            "metric_name": "context_relevance"
        },
    ]

    for cf in counterfactuals:
        cursor.execute("""
            INSERT INTO raia_counterfactual_scenarios (
                run_id, scenario_name, modification_type, parameter_changed,
                original_value, counterfactual_value, original_score,
                counterfactual_score, score_difference, metric_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cf["run_id"], cf["scenario_name"], cf["modification_type"],
            cf["parameter_changed"], cf["original_value"], cf["counterfactual_value"],
            cf["original_score"], cf["counterfactual_score"], cf["score_difference"],
            cf["metric_name"], datetime.now().isoformat()
        ))

    # Sensitivity analyses
    sensitivities = [
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "parameter_name": "chunk_overlap",
            "base_value": "50",
            "test_value": "100",
            "base_score": 0.76,
            "test_score": 0.79,
            "sensitivity": 0.03,
            "metric_name": "retrieval_precision"
        },
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "parameter_name": "max_tokens",
            "base_value": "150",
            "test_value": "300",
            "base_score": 0.71,
            "test_score": 0.83,
            "sensitivity": 0.12,
            "metric_name": "answer_completeness"
        },
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "parameter_name": "embedding_model",
            "base_value": "text-embedding-ada-002",
            "test_value": "text-embedding-3-large",
            "base_score": 0.74,
            "test_score": 0.88,
            "sensitivity": 0.14,
            "metric_name": "semantic_similarity"
        },
    ]

    for sens in sensitivities:
        cursor.execute("""
            INSERT INTO raia_sensitivity_analyses (
                run_id, parameter_name, base_value, test_value,
                base_score, test_score, sensitivity, metric_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sens["run_id"], sens["parameter_name"], sens["base_value"],
            sens["test_value"], sens["base_score"], sens["test_score"],
            sens["sensitivity"], sens["metric_name"], datetime.now().isoformat()
        ))

    # Optimization recommendations
    optimizations = [
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_type": "parameter_tuning",
            "category": "retrieval",
            "parameter": "top_k",
            "current_value": "3",
            "recommended_value": "5",
            "expected_improvement": 0.06,
            "confidence": 0.85,
            "priority": "high",
            "rationale": "Increasing top_k from 3 to 5 documents improves context coverage without significant quality degradation"
        },
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_type": "model_config",
            "category": "generation",
            "parameter": "temperature",
            "current_value": "0.7",
            "recommended_value": "0.4",
            "expected_improvement": 0.08,
            "confidence": 0.92,
            "priority": "high",
            "rationale": "Lower temperature reduces hallucinations and improves factual accuracy"
        },
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_type": "architecture",
            "category": "embedding",
            "parameter": "chunk_size",
            "current_value": "512",
            "recommended_value": "768",
            "expected_improvement": 0.04,
            "confidence": 0.78,
            "priority": "medium",
            "rationale": "Slightly larger chunks maintain better semantic coherence"
        },
    ]

    for opt in optimizations:
        cursor.execute("""
            INSERT INTO raia_optimization_recommendations (
                run_id, recommendation_type, category, parameter,
                current_value, recommended_value, expected_improvement,
                confidence, priority, rationale, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opt["run_id"], opt["recommendation_type"], opt["category"],
            opt["parameter"], opt["current_value"], opt["recommended_value"],
            opt["expected_improvement"], opt["confidence"], opt["priority"],
            opt["rationale"], datetime.now().isoformat()
        ))

    conn.commit()
    print(f"✅ Added {len(counterfactuals)} counterfactual scenarios")
    print(f"✅ Added {len(sensitivities)} sensitivity analyses")
    print(f"✅ Added {len(optimizations)} optimization recommendations")


def main():
    """Main execution."""
    print("=" * 60)
    print("POPULATING MISSING DATA FOR RAIA PLATFORM")
    print("=" * 60)

    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)

        # Populate drift metrics
        populate_drift_metrics(conn)

        # Populate what-if analysis data
        populate_whatif_data(conn)

        print("\n" + "=" * 60)
        print("✅ DATA POPULATION COMPLETE!")
        print("=" * 60)
        print("\nRefresh your browser to see the new data in:")
        print("  • System Monitoring (drift metrics)")
        print("  • What-If Analysis (counterfactuals, sensitivity, optimizations)")

        conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
