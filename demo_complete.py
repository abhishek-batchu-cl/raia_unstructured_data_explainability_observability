#!/usr/bin/env python3
"""
RAIA Complete Demo

End-to-end demonstration of all RAIA capabilities:
1. RAG Evaluation (retrieval, answer quality, drift, pipeline)
2. Explainability (attribution, reasoning traces)
3. What-If Analysis (counterfactual scenarios)
4. Comparison & Reporting (benchmarking, reports)

Shows the complete evaluation workflow for production RAG systems.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from raia import (
    RAIARAGInspector,
    SQLiteRAIAStorage,
    RAIAComparator,
    Attribution,
    ReasoningStep,
)


def print_header(title: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str) -> None:
    """Print formatted section."""
    print(f"\n--- {title} ---\n")


def simulate_rag_evaluation():
    """Simulate RAG system evaluation with multiple runs."""
    print_header("STEP 1: RAG System Evaluation")

    storage = SQLiteRAIAStorage("demo_complete.db")
    inspector = RAIARAGInspector(storage=storage)

    # Simulate 3 different RAG configurations
    configs = [
        {
            "run_id": "config_baseline",
            "name": "Baseline (GPT-4, 5 docs)",
            "retrieval": {"num_docs": 5, "rerank": True},
            "llm": "gpt-4",
            "queries": [
                {"quality": 0.92, "latency": 2200, "cost": 0.015},
                {"quality": 0.94, "latency": 2100, "cost": 0.014},
                {"quality": 0.91, "latency": 2300, "cost": 0.016},
            ],
        },
        {
            "run_id": "config_optimized",
            "name": "Optimized (GPT-3.5, 3 docs, cache)",
            "retrieval": {"num_docs": 3, "rerank": True, "cache": True},
            "llm": "gpt-3.5-turbo",
            "queries": [
                {"quality": 0.87, "latency": 950, "cost": 0.0018},
                {"quality": 0.89, "latency": 920, "cost": 0.0017},
                {"quality": 0.85, "latency": 980, "cost": 0.0019},
            ],
        },
        {
            "run_id": "config_balanced",
            "name": "Balanced (GPT-4-turbo, 4 docs)",
            "retrieval": {"num_docs": 4, "rerank": True},
            "llm": "gpt-4-turbo",
            "queries": [
                {"quality": 0.90, "latency": 1400, "cost": 0.0045},
                {"quality": 0.91, "latency": 1350, "cost": 0.0042},
                {"quality": 0.89, "latency": 1450, "cost": 0.0048},
            ],
        },
    ]

    print("Evaluating 3 different RAG configurations...\n")

    for config in configs:
        print(f"📊 {config['name']}")
        print(f"   Configuration: {config['retrieval']}, LLM: {config['llm']}")

        # Track answer quality for each query
        for i, query_metrics in enumerate(config["queries"], 1):
            inspector.track_answer_quality(
                run_id=config["run_id"],
                query=f"Sample query {i}",
                answer=f"Sample answer {i}",
                answer_relevance=query_metrics["quality"],
                answer_completeness=query_metrics["quality"],
                answer_faithfulness=0.96,
                hallucination_score=0.04,
                generation_latency_ms=query_metrics["latency"],
                metadata={"cost_usd": query_metrics["cost"]},
            )

        avg_quality = sum(q["quality"] for q in config["queries"]) / len(config["queries"])
        avg_latency = sum(q["latency"] for q in config["queries"]) / len(config["queries"])
        avg_cost = sum(q["cost"] for q in config["queries"]) / len(config["queries"])

        print(f"   Quality: {avg_quality:.2%}, Latency: {avg_latency:.0f}ms, Cost: ${avg_cost:.6f}")

    print("\n✅ Evaluation complete for all configurations")
    return [c["run_id"] for c in configs], configs


def demonstrate_explainability():
    """Demonstrate explainability features."""
    print_header("STEP 2: Explainability Analysis")

    storage = SQLiteRAIAStorage("demo_complete.db")
    inspector = RAIARAGInspector(storage=storage)

    run_id = "explain_demo"

    print_section("Attribution Tracking")
    print("Tracking which documents contributed to the answer...\n")

    # Example attribution
    attributions = [
        Attribution(
            answer_span="machine learning model",
            answer_start_idx=0,
            answer_end_idx=22,
            source_doc_id="ml_textbook_ch3",
            source_span="supervised learning models",
            source_start_idx=45,
            source_end_idx=71,
            confidence=0.94,
            similarity_score=0.91,
        ),
    ]

    attribution_map = inspector.track_attribution(
        run_id=run_id,
        query="Explain machine learning",
        answer="A machine learning model learns patterns from data...",
        attributions=attributions,
        overall_confidence=0.94,
        faithfulness_score=0.97,
        hallucination_score=0.03,
        total_context_tokens=500,
        utilized_context_tokens=425,
    )

    print(f"✅ Faithfulness: {attribution_map.faithfulness_score:.2%}")
    print(f"✅ Hallucination: {attribution_map.hallucination_score:.2%}")
    print(f"✅ Context efficiency: {attribution_map.context_efficiency:.2%}")

    print_section("Reasoning Trace")
    print("Capturing step-by-step reasoning process...\n")

    # Example reasoning steps
    base_time = datetime.utcnow()
    steps = [
        ReasoningStep(
            step_number=1,
            step_name="Query Understanding",
            step_type="understanding",
            description="Extracted intent and key concepts",
            rationale="Need to understand query before retrieval",
            confidence=0.93,
            inputs={},
            outputs={},
            start_time=base_time,
            end_time=base_time,
            latency_ms=45.0,
            success=True,
        ),
    ]

    reasoning_trace = inspector.track_reasoning(
        run_id=run_id,
        trace_type="rag_reasoning",
        query="Explain machine learning",
        steps=steps,
        final_answer="A machine learning model...",
        reasoning_quality_score=0.93,
        logical_consistency=0.96,
    )

    print(f"✅ Reasoning quality: {reasoning_trace.reasoning_quality_score:.2%}")
    print(f"✅ Logical consistency: {reasoning_trace.logical_consistency:.2%}")
    print(f"✅ Total steps: {reasoning_trace.total_steps}")


def demonstrate_whatif():
    """Demonstrate what-if analysis."""
    print_header("STEP 3: What-If Analysis")

    storage = SQLiteRAIAStorage("demo_complete.db")
    inspector = RAIARAGInspector(storage=storage)

    run_id = "whatif_demo"

    print("Simulating: What if we reduce context size?\n")

    scenario = inspector.simulate_scenario(
        run_id=run_id,
        scenario_name="Reduce context for cost savings",
        scenario_type="context",
        original_config={"context_tokens": 2000},
        alternative_config={"context_tokens": 1200},
        original_quality=0.91,
        original_latency_ms=1800.0,
        original_cost_usd=0.0045,
        alternative_quality=0.90,
        alternative_latency_ms=1100.0,
        alternative_cost_usd=0.0027,
    )

    print(f"Quality change:  {scenario.quality_delta_pct:+.1f}%")
    print(f"Latency change:  {scenario.latency_delta_pct:+.1f}%")
    print(f"Cost change:     {scenario.cost_delta_pct:+.1f}%")
    print(f"\n✅ Recommendation: {scenario.recommendation.upper()}")
    print(f"   {scenario.recommendation_rationale}")


def compare_and_report():
    """Compare runs and generate report."""
    print_header("STEP 4: Comparison & Reporting")

    storage = SQLiteRAIAStorage("demo_complete.db")
    comparator = RAIAComparator(storage)

    run_ids = ["config_baseline", "config_optimized", "config_balanced"]

    print_section("A/B/C Comparison")
    comparison = comparator.compare_runs(
        run_ids=run_ids,
        comparison_name="RAG Configuration Comparison"
    )

    comparator.print_comparison(comparison)

    print_section("Comprehensive Report")
    report = comparator.generate_report(
        run_ids=run_ids,
        report_name="RAG System Evaluation Report - Q4 2024"
    )

    comparator.print_report(report)


def main():
    """Run complete RAIA demo."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  RAIA COMPLETE DEMO".center(78) + "║")
    print("║" + "  End-to-End Evaluation for Production RAG Systems".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run all demos
    run_ids, configs = simulate_rag_evaluation()
    demonstrate_explainability()
    demonstrate_whatif()
    compare_and_report()

    # Final summary
    print_header("SUMMARY: Complete RAIA Workflow")

    print("✅ Phase 1: RAG Evaluation")
    print("   • Evaluated 3 configurations with 3 queries each")
    print("   • Tracked quality, latency, cost metrics")
    print("   • Identified best configuration for different goals")

    print("\n✅ Phase 2: Explainability")
    print("   • Attribution tracking (document → answer mapping)")
    print("   • Reasoning traces (step-by-step process)")
    print("   • Faithfulness and hallucination detection")

    print("\n✅ Phase 3: What-If Analysis")
    print("   • Counterfactual scenarios simulation")
    print("   • Trade-off analysis (quality vs cost vs latency)")
    print("   • Actionable recommendations with confidence")

    print("\n✅ Phase 4: Comparison & Reporting")
    print("   • Side-by-side comparison of configurations")
    print("   • Winner determination with rationale")
    print("   • Comprehensive evaluation report with insights")

    print("\n" + "=" * 80)
    print("  KEY TAKEAWAYS")
    print("=" * 80)

    print("\n1. COMPREHENSIVE EVALUATION")
    print("   RAIA provides end-to-end evaluation from metrics to insights")

    print("\n2. EXPLAINABILITY")
    print("   Understand not just WHAT happened, but WHY and HOW")

    print("\n3. PROACTIVE OPTIMIZATION")
    print("   Simulate changes before implementing with what-if analysis")

    print("\n4. DATA-DRIVEN DECISIONS")
    print("   Compare configurations and generate actionable reports")

    print("\n5. PRODUCTION-READY")
    print("   All metrics persisted, queryable, and ready for monitoring")

    print("\n✅ Demo completed successfully!")
    print(f"✅ Database: demo_complete.db")
    print("\nTo clean up:")
    print("  rm demo_complete.db\n")


if __name__ == "__main__":
    main()
