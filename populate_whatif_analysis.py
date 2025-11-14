#!/usr/bin/env python3
"""
Populate What-If Analysis data with realistic scenarios.
Includes counterfactual scenarios, sensitivity analysis, and optimization recommendations.
"""

import sqlite3
import json
from datetime import datetime
import uuid

DB_PATH = "complete_end_to_end_demo.db"

def populate_counterfactual_scenarios(conn):
    """Add realistic counterfactual scenarios."""
    print("🔄 Populating counterfactual scenarios...")

    cursor = conn.cursor()

    scenarios = [
        {
            "run_id": f"cf_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Increase Chunk Size to 1024",
            "scenario_type": "chunk_size_optimization",
            "original_config": json.dumps({
                "chunk_size": 512,
                "chunk_overlap": 50,
                "embedding_model": "text-embedding-ada-002"
            }),
            "alternative_config": json.dumps({
                "chunk_size": 1024,
                "chunk_overlap": 50,
                "embedding_model": "text-embedding-ada-002"
            }),
            "original_quality": 0.78,
            "original_latency_ms": 450.0,
            "original_cost_usd": 0.0012,
            "original_metadata": json.dumps({"retrieval_precision": 0.76, "answer_relevance": 0.80}),
            "alternative_quality": 0.85,
            "alternative_latency_ms": 520.0,
            "alternative_cost_usd": 0.0015,
            "alternative_metadata": json.dumps({"retrieval_precision": 0.83, "answer_relevance": 0.87}),
            "quality_delta": 0.07,
            "quality_delta_pct": 8.97,
            "latency_delta_ms": 70.0,
            "latency_delta_pct": 15.56,
            "cost_delta_usd": 0.0003,
            "cost_delta_pct": 25.0,
            "is_improvement": True,
            "recommendation": "Consider increasing chunk size for better context",
            "recommendation_rationale": "Larger chunks provide more context per retrieval, improving answer quality by 9% with acceptable latency increase",
            "confidence": 0.87,
            "pros": json.dumps([
                "9% improvement in answer quality",
                "Better semantic coherence",
                "Reduced number of chunks to index"
            ]),
            "cons": json.dumps([
                "16% increase in latency",
                "25% higher embedding costs",
                "May include irrelevant context"
            ])
        },
        {
            "run_id": f"cf_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Lower Temperature to 0.3",
            "scenario_type": "model_parameter_tuning",
            "original_config": json.dumps({
                "temperature": 0.7,
                "max_tokens": 150,
                "model": "gpt-3.5-turbo"
            }),
            "alternative_config": json.dumps({
                "temperature": 0.3,
                "max_tokens": 150,
                "model": "gpt-3.5-turbo"
            }),
            "original_quality": 0.72,
            "original_latency_ms": 380.0,
            "original_cost_usd": 0.0008,
            "original_metadata": json.dumps({"factual_accuracy": 0.70, "hallucination_rate": 0.15}),
            "alternative_quality": 0.81,
            "alternative_latency_ms": 380.0,
            "alternative_cost_usd": 0.0008,
            "alternative_metadata": json.dumps({"factual_accuracy": 0.85, "hallucination_rate": 0.06}),
            "quality_delta": 0.09,
            "quality_delta_pct": 12.5,
            "latency_delta_ms": 0.0,
            "latency_delta_pct": 0.0,
            "cost_delta_usd": 0.0,
            "cost_delta_pct": 0.0,
            "is_improvement": True,
            "recommendation": "Strongly recommended: Lower temperature to 0.3",
            "recommendation_rationale": "Reduces hallucinations by 60% and improves factual accuracy by 21% with no cost or latency impact",
            "confidence": 0.95,
            "pros": json.dumps([
                "12.5% quality improvement",
                "60% reduction in hallucinations",
                "No additional cost",
                "Same latency"
            ]),
            "cons": json.dumps([
                "Less creative responses",
                "More deterministic output"
            ])
        },
        {
            "run_id": f"cf_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Increase Retrieved Documents to 5",
            "scenario_type": "retrieval_optimization",
            "original_config": json.dumps({
                "top_k": 3,
                "similarity_threshold": 0.7,
                "retrieval_method": "semantic"
            }),
            "alternative_config": json.dumps({
                "top_k": 5,
                "similarity_threshold": 0.7,
                "retrieval_method": "semantic"
            }),
            "original_quality": 0.75,
            "original_latency_ms": 320.0,
            "original_cost_usd": 0.0010,
            "original_metadata": json.dumps({"context_coverage": 0.72, "context_relevance": 0.78}),
            "alternative_quality": 0.79,
            "alternative_latency_ms": 410.0,
            "alternative_cost_usd": 0.0014,
            "alternative_metadata": json.dumps({"context_coverage": 0.85, "context_relevance": 0.75}),
            "quality_delta": 0.04,
            "quality_delta_pct": 5.33,
            "latency_delta_ms": 90.0,
            "latency_delta_pct": 28.13,
            "cost_delta_usd": 0.0004,
            "cost_delta_pct": 40.0,
            "is_improvement": False,
            "recommendation": "Keep current top_k=3 setting",
            "recommendation_rationale": "Marginal 5% quality gain doesn't justify 28% latency increase and 40% cost increase",
            "confidence": 0.82,
            "pros": json.dumps([
                "5% quality improvement",
                "Better context coverage"
            ]),
            "cons": json.dumps([
                "28% higher latency",
                "40% increased costs",
                "Potential context dilution"
            ])
        },
        {
            "run_id": f"cf_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Upgrade to GPT-4",
            "scenario_type": "model_upgrade",
            "original_config": json.dumps({
                "model": "gpt-3.5-turbo",
                "temperature": 0.5,
                "max_tokens": 150
            }),
            "alternative_config": json.dumps({
                "model": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 150
            }),
            "original_quality": 0.76,
            "original_latency_ms": 400.0,
            "original_cost_usd": 0.0009,
            "original_metadata": json.dumps({"reasoning_quality": 0.74, "comprehension": 0.78}),
            "alternative_quality": 0.92,
            "alternative_latency_ms": 850.0,
            "alternative_cost_usd": 0.0045,
            "alternative_metadata": json.dumps({"reasoning_quality": 0.94, "comprehension": 0.90}),
            "quality_delta": 0.16,
            "quality_delta_pct": 21.05,
            "latency_delta_ms": 450.0,
            "latency_delta_pct": 112.5,
            "cost_delta_usd": 0.0036,
            "cost_delta_pct": 400.0,
            "is_improvement": True,
            "recommendation": "Consider GPT-4 for high-value use cases",
            "recommendation_rationale": "Significant 21% quality improvement but with substantial cost and latency trade-offs. Best for complex queries where quality is paramount.",
            "confidence": 0.88,
            "pros": json.dumps([
                "21% quality improvement",
                "27% better reasoning",
                "15% better comprehension",
                "Handles complex queries better"
            ]),
            "cons": json.dumps([
                "400% cost increase",
                "112% higher latency",
                "May be overkill for simple queries"
            ])
        },
        {
            "run_id": f"cf_run_{uuid.uuid4().hex[:8]}",
            "scenario_name": "Hybrid Retrieval (Semantic + Keyword)",
            "scenario_type": "retrieval_method",
            "original_config": json.dumps({
                "retrieval_method": "semantic",
                "top_k": 3
            }),
            "alternative_config": json.dumps({
                "retrieval_method": "hybrid",
                "semantic_weight": 0.7,
                "keyword_weight": 0.3,
                "top_k": 3
            }),
            "original_quality": 0.74,
            "original_latency_ms": 310.0,
            "original_cost_usd": 0.0010,
            "original_metadata": json.dumps({"recall": 0.72, "precision": 0.76}),
            "alternative_quality": 0.82,
            "alternative_latency_ms": 380.0,
            "alternative_cost_usd": 0.0011,
            "alternative_metadata": json.dumps({"recall": 0.84, "precision": 0.80}),
            "quality_delta": 0.08,
            "quality_delta_pct": 10.81,
            "latency_delta_ms": 70.0,
            "latency_delta_pct": 22.58,
            "cost_delta_usd": 0.0001,
            "cost_delta_pct": 10.0,
            "is_improvement": True,
            "recommendation": "Implement hybrid retrieval",
            "recommendation_rationale": "11% quality improvement with minimal cost increase (10%) and acceptable latency trade-off. Combines best of semantic and keyword search.",
            "confidence": 0.91,
            "pros": json.dumps([
                "11% quality improvement",
                "Better recall (17% higher)",
                "Handles both conceptual and exact matches",
                "Only 10% cost increase"
            ]),
            "cons": json.dumps([
                "23% higher latency",
                "More complex implementation",
                "Requires tuning weight parameters"
            ])
        }
    ]

    for scenario in scenarios:
        cursor.execute("""
            INSERT INTO raia_counterfactual_scenarios (
                run_id, scenario_name, scenario_type,
                original_config, alternative_config,
                original_quality, original_latency_ms, original_cost_usd, original_metadata,
                alternative_quality, alternative_latency_ms, alternative_cost_usd, alternative_metadata,
                quality_delta, quality_delta_pct,
                latency_delta_ms, latency_delta_pct,
                cost_delta_usd, cost_delta_pct,
                is_improvement, recommendation, recommendation_rationale, confidence,
                pros, cons, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scenario["run_id"], scenario["scenario_name"], scenario["scenario_type"],
            scenario["original_config"], scenario["alternative_config"],
            scenario["original_quality"], scenario["original_latency_ms"],
            scenario["original_cost_usd"], scenario["original_metadata"],
            scenario["alternative_quality"], scenario["alternative_latency_ms"],
            scenario["alternative_cost_usd"], scenario["alternative_metadata"],
            scenario["quality_delta"], scenario["quality_delta_pct"],
            scenario["latency_delta_ms"], scenario["latency_delta_pct"],
            scenario["cost_delta_usd"], scenario["cost_delta_pct"],
            scenario["is_improvement"], scenario["recommendation"],
            scenario["recommendation_rationale"], scenario["confidence"],
            scenario["pros"], scenario["cons"],
            datetime.now().isoformat(), json.dumps({"generated_by": "whatif_analysis_v1"})
        ))

    conn.commit()
    print(f"✅ Added {len(scenarios)} counterfactual scenarios")


def populate_sensitivity_analyses(conn):
    """Add sensitivity analysis results."""
    print("\n🔄 Populating sensitivity analyses...")

    cursor = conn.cursor()

    analyses = [
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "analysis_name": "Chunk Size Sensitivity Analysis",
            "parameters": json.dumps({
                "chunk_sizes_tested": [256, 512, 768, 1024, 1536],
                "quality_scores": [0.72, 0.78, 0.82, 0.85, 0.83],
                "latency_scores": [380, 450, 490, 520, 580],
                "baseline": 512
            }),
            "most_sensitive_param": "chunk_size",
            "least_sensitive_param": "chunk_overlap",
            "optimal_config": json.dumps({
                "chunk_size": 1024,
                "chunk_overlap": 50,
                "expected_quality": 0.85,
                "expected_latency_ms": 520
            }),
            "expected_improvement": 0.07,
            "num_simulations": 25,
            "analysis_duration_ms": 45000.0
        },
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "analysis_name": "Temperature Parameter Sweep",
            "parameters": json.dumps({
                "temperatures_tested": [0.0, 0.3, 0.5, 0.7, 1.0],
                "quality_scores": [0.84, 0.81, 0.76, 0.72, 0.65],
                "creativity_scores": [0.3, 0.6, 0.75, 0.85, 0.95],
                "hallucination_rates": [0.02, 0.06, 0.12, 0.15, 0.25],
                "baseline": 0.7
            }),
            "most_sensitive_param": "temperature",
            "least_sensitive_param": "top_p",
            "optimal_config": json.dumps({
                "temperature": 0.3,
                "top_p": 0.9,
                "expected_quality": 0.81,
                "hallucination_rate": 0.06
            }),
            "expected_improvement": 0.09,
            "num_simulations": 20,
            "analysis_duration_ms": 32000.0
        },
        {
            "run_id": f"sens_run_{uuid.uuid4().hex[:8]}",
            "analysis_name": "Retrieval Top-K Analysis",
            "parameters": json.dumps({
                "top_k_values": [1, 3, 5, 7, 10],
                "quality_scores": [0.68, 0.75, 0.79, 0.77, 0.74],
                "latency_scores": [280, 320, 410, 530, 680],
                "cost_per_query": [0.0007, 0.0010, 0.0014, 0.0018, 0.0024],
                "baseline": 3
            }),
            "most_sensitive_param": "top_k",
            "least_sensitive_param": "similarity_threshold",
            "optimal_config": json.dumps({
                "top_k": 5,
                "similarity_threshold": 0.7,
                "expected_quality": 0.79,
                "expected_cost": 0.0014
            }),
            "expected_improvement": 0.04,
            "num_simulations": 30,
            "analysis_duration_ms": 52000.0
        }
    ]

    for analysis in analyses:
        cursor.execute("""
            INSERT INTO raia_sensitivity_analyses (
                run_id, analysis_name, parameters,
                most_sensitive_param, least_sensitive_param, optimal_config,
                expected_improvement, num_simulations, analysis_duration_ms,
                created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis["run_id"], analysis["analysis_name"], analysis["parameters"],
            analysis["most_sensitive_param"], analysis["least_sensitive_param"],
            analysis["optimal_config"], analysis["expected_improvement"],
            analysis["num_simulations"], analysis["analysis_duration_ms"],
            datetime.now().isoformat(), json.dumps({"analysis_type": "parameter_sweep"})
        ))

    conn.commit()
    print(f"✅ Added {len(analyses)} sensitivity analyses")


def populate_optimization_recommendations(conn):
    """Add optimization recommendations."""
    print("\n🔄 Populating optimization recommendations...")

    cursor = conn.cursor()

    recommendations = [
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_name": "Implement Hybrid Retrieval + Lower Temperature",
            "optimization_goal": "Maximize quality while keeping costs reasonable",
            "current_quality": 0.74,
            "current_latency_ms": 380.0,
            "current_cost_usd": 0.0010,
            "recommended_changes": json.dumps({
                "retrieval": "hybrid (semantic 70% + keyword 30%)",
                "temperature": "0.3 (down from 0.7)",
                "chunk_size": "1024 (up from 512)"
            }),
            "expected_quality": 0.88,
            "expected_latency_ms": 520.0,
            "expected_cost_usd": 0.0015,
            "quality_improvement_pct": 18.92,
            "latency_improvement_pct": -36.84,  # negative = slower
            "cost_savings_pct": -50.0,  # negative = more expensive
            "implementation_difficulty": "medium",
            "implementation_steps": json.dumps([
                "1. Implement hybrid retrieval combining BM25 and vector search",
                "2. Tune semantic/keyword weights (start 70/30, adjust based on results)",
                "3. Update chunk size to 1024 tokens with 100 token overlap",
                "4. Lower temperature to 0.3 in generation config",
                "5. Run A/B test on 10% of traffic for 1 week",
                "6. Monitor quality metrics and user feedback",
                "7. Gradually roll out to 100% if successful"
            ]),
            "estimated_implementation_time": "2-3 weeks",
            "risk_level": "low",
            "risks": json.dumps([
                "Higher latency may impact user experience",
                "Cost increase of 50% needs budget approval",
                "Hybrid retrieval requires additional infrastructure"
            ]),
            "mitigation_strategies": json.dumps([
                "Implement caching for frequently asked questions",
                "Use async processing for non-critical queries",
                "Monitor cost metrics closely and set alerts",
                "Prepare rollback plan if metrics degrade"
            ]),
            "priority": "high",
            "priority_rationale": "19% quality improvement significantly enhances user experience. Cost increase is acceptable given quality gains. Latency impact can be mitigated with caching.",
            "estimated_annual_savings_usd": -18000.0,  # negative = cost increase
            "estimated_roi_pct": 240.0  # based on improved user satisfaction
        },
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_name": "Temperature Optimization Only (Quick Win)",
            "optimization_goal": "Quick quality improvement with zero cost impact",
            "current_quality": 0.72,
            "current_latency_ms": 380.0,
            "current_cost_usd": 0.0008,
            "recommended_changes": json.dumps({
                "temperature": "0.3 (down from 0.7)",
                "note": "Simple config change, no infrastructure changes"
            }),
            "expected_quality": 0.81,
            "expected_latency_ms": 380.0,
            "expected_cost_usd": 0.0008,
            "quality_improvement_pct": 12.5,
            "latency_improvement_pct": 0.0,
            "cost_savings_pct": 0.0,
            "implementation_difficulty": "easy",
            "implementation_steps": json.dumps([
                "1. Update temperature parameter in config file",
                "2. Deploy configuration change",
                "3. Monitor hallucination rates and factual accuracy",
                "4. Collect user feedback for 3 days",
                "5. Confirm improvement in metrics"
            ]),
            "estimated_implementation_time": "1 day",
            "risk_level": "very_low",
            "risks": json.dumps([
                "Responses may be less creative",
                "More predictable outputs"
            ]),
            "mitigation_strategies": json.dumps([
                "Easy to revert if needed",
                "Test on staging first",
                "Monitor user feedback closely"
            ]),
            "priority": "high",
            "priority_rationale": "Zero cost, zero effort change that improves quality by 12.5%. No downside. Should be implemented immediately as a quick win.",
            "estimated_annual_savings_usd": 0.0,
            "estimated_roi_pct": 999.0  # essentially infinite ROI for zero cost
        },
        {
            "run_id": f"opt_run_{uuid.uuid4().hex[:8]}",
            "recommendation_name": "Selective GPT-4 for Complex Queries",
            "optimization_goal": "Balance quality and cost by using right model for right query",
            "current_quality": 0.76,
            "current_latency_ms": 400.0,
            "current_cost_usd": 0.0009,
            "recommended_changes": json.dumps({
                "routing": "Use GPT-4 for complex queries (20%), GPT-3.5 for simple (80%)",
                "complexity_classifier": "Train classifier to route queries",
                "fallback": "GPT-4 if GPT-3.5 confidence < 0.7"
            }),
            "expected_quality": 0.84,
            "expected_latency_ms": 490.0,
            "expected_cost_usd": 0.0016,
            "quality_improvement_pct": 10.53,
            "latency_improvement_pct": -22.5,
            "cost_savings_pct": -77.78,
            "implementation_difficulty": "hard",
            "implementation_steps": json.dumps([
                "1. Collect dataset of queries labeled by complexity",
                "2. Train query complexity classifier",
                "3. Implement routing logic based on classifier",
                "4. Set up monitoring for both models",
                "5. Implement fallback mechanism",
                "6. A/B test routing vs always GPT-3.5",
                "7. Fine-tune complexity threshold",
                "8. Roll out gradually"
            ]),
            "estimated_implementation_time": "4-6 weeks",
            "risk_level": "medium",
            "risks": json.dumps([
                "Classifier may misroute queries",
                "Cost unpredictability if routing changes",
                "Complexity in maintaining two models",
                "Latency increase for complex queries"
            ]),
            "mitigation_strategies": json.dumps([
                "Start with conservative routing (10% GPT-4)",
                "Implement strict cost caps",
                "Monitor classification accuracy closely",
                "Provide manual override for specific query types"
            ]),
            "priority": "medium",
            "priority_rationale": "Good quality improvement but significant cost increase and implementation complexity. Worth considering if budget allows and complex queries are common.",
            "estimated_annual_savings_usd": -28000.0,
            "estimated_roi_pct": 156.0
        }
    ]

    for rec in recommendations:
        cursor.execute("""
            INSERT INTO raia_optimization_recommendations (
                run_id, recommendation_name, optimization_goal,
                current_quality, current_latency_ms, current_cost_usd,
                recommended_changes,
                expected_quality, expected_latency_ms, expected_cost_usd,
                quality_improvement_pct, latency_improvement_pct, cost_savings_pct,
                implementation_difficulty, implementation_steps, estimated_implementation_time,
                risk_level, risks, mitigation_strategies,
                priority, priority_rationale,
                estimated_annual_savings_usd, estimated_roi_pct,
                created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec["run_id"], rec["recommendation_name"], rec["optimization_goal"],
            rec["current_quality"], rec["current_latency_ms"], rec["current_cost_usd"],
            rec["recommended_changes"],
            rec["expected_quality"], rec["expected_latency_ms"], rec["expected_cost_usd"],
            rec["quality_improvement_pct"], rec["latency_improvement_pct"], rec["cost_savings_pct"],
            rec["implementation_difficulty"], rec["implementation_steps"], rec["estimated_implementation_time"],
            rec["risk_level"], rec["risks"], rec["mitigation_strategies"],
            rec["priority"], rec["priority_rationale"],
            rec["estimated_annual_savings_usd"], rec["estimated_roi_pct"],
            datetime.now().isoformat(), json.dumps({"analysis_version": "v1.0"})
        ))

    conn.commit()
    print(f"✅ Added {len(recommendations)} optimization recommendations")


def main():
    """Main execution."""
    print("=" * 70)
    print("POPULATING WHAT-IF ANALYSIS DATA")
    print("=" * 70)

    try:
        conn = sqlite3.connect(DB_PATH)

        # Populate all what-if analysis data
        populate_counterfactual_scenarios(conn)
        populate_sensitivity_analyses(conn)
        populate_optimization_recommendations(conn)

        print("\n" + "=" * 70)
        print("✅ WHAT-IF ANALYSIS DATA POPULATION COMPLETE!")
        print("=" * 70)
        print("\nRefresh your browser at http://localhost:5173/whatif")
        print("\nYou should now see:")
        print("  • 5 Counterfactual Scenarios")
        print("  • 3 Sensitivity Analyses")
        print("  • 3 Optimization Recommendations")

        conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
