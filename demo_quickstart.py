#!/usr/bin/env python3
"""
RAIA Quick Start Demo
=====================

A focused 2-minute demo showing RAIA's core capabilities:
1. Track RAG metrics (retrieval + answer quality)
2. Explainability (attribution + reasoning)
3. What-If analysis (optimization scenarios)
4. Comparison (A/B testing)

Perfect for first-time users!
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


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def main():
    """Run quick start demo."""
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                            ║")
    print("║                      RAIA QUICK START DEMO                                 ║")
    print("║         Responsible AI Analytics & Agent Evaluation                        ║")
    print("║                                                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝\n")

    # Initialize
    storage = SQLiteRAIAStorage("quickstart_demo.db")
    inspector = RAIARAGInspector(storage=storage)

    # ========================================================================
    # 1. RAG METRICS TRACKING
    # ========================================================================
    print_header("1. RAG Metrics Tracking")

    print("Scenario: Evaluating 2 RAG configurations\n")

    # Configuration A: High quality, high cost
    print("📊 Configuration A (GPT-4, 5 documents)")
    for i in range(3):
        inspector.track_retrieval(
            run_id="config_a",
            query=f"Climate query {i+1}",
            retrieved_doc_ids=[f"doc_{j}" for j in range(5)],
            relevance_scores=[0.92, 0.89, 0.87, 0.85, 0.82],
            retrieval_latency_ms=65.0,
            precision_at_k=0.95,
            recall_at_k=0.88,
        )

        inspector.track_answer_quality(
            run_id="config_a",
            query=f"Climate query {i+1}",
            answer="Detailed answer about climate...",
            answer_relevance=0.93,
            answer_completeness=0.91,
            answer_faithfulness=0.96,
            hallucination_score=0.04,
            generation_latency_ms=2100.0,
            metadata={"cost_usd": 0.015},
        )

    print("   Quality: 93%, Latency: 2100ms, Cost: $0.015")

    # Configuration B: Good quality, lower cost
    print("\n📊 Configuration B (GPT-3.5-Turbo, 3 documents)")
    for i in range(3):
        inspector.track_retrieval(
            run_id="config_b",
            query=f"Climate query {i+1}",
            retrieved_doc_ids=[f"doc_{j}" for j in range(3)],
            relevance_scores=[0.89, 0.86, 0.83],
            retrieval_latency_ms=45.0,
            precision_at_k=0.90,
            recall_at_k=0.82,
        )

        inspector.track_answer_quality(
            run_id="config_b",
            query=f"Climate query {i+1}",
            answer="Concise answer about climate...",
            answer_relevance=0.87,
            answer_completeness=0.85,
            answer_faithfulness=0.94,
            hallucination_score=0.06,
            generation_latency_ms=950.0,
            metadata={"cost_usd": 0.002},
        )

    print("   Quality: 87%, Latency: 950ms, Cost: $0.002")

    print("\n✅ Metrics tracked for both configurations")

    # ========================================================================
    # 2. EXPLAINABILITY
    # ========================================================================
    print_header("2. Explainability")

    print("Tracking WHERE answers come from (attribution)...\n")

    attribution = Attribution(
        answer_span="greenhouse gas emissions",
        answer_start_idx=0,
        answer_end_idx=24,
        source_doc_id="ipcc_report_ch2",
        source_span="anthropogenic greenhouse gas emissions",
        source_start_idx=12,
        source_end_idx=50,
        confidence=0.94,
        similarity_score=0.91,
    )

    attribution_map = inspector.track_attribution(
        run_id="config_a",
        query="What causes climate change?",
        answer="Greenhouse gas emissions from human activities...",
        attributions=[attribution],
        overall_confidence=0.94,
        faithfulness_score=0.97,
        hallucination_score=0.03,
        total_context_tokens=800,
        utilized_context_tokens=720,
    )

    print(f"✅ Faithfulness: {attribution_map.faithfulness_score:.0%}")
    print(f"✅ Context efficiency: {attribution_map.context_efficiency:.0%}")
    print(f"✅ Primary source: {attribution_map.primary_source}")

    print("\nTracking HOW reasoning happens (reasoning trace)...\n")

    base_time = datetime.utcnow()
    step = ReasoningStep(
        step_number=1,
        step_name="Query Analysis",
        step_type="understanding",
        description="Extracted key concepts: climate, causes",
        rationale="Need to identify query intent",
        confidence=0.93,
        inputs={},
        outputs={},
        start_time=base_time,
        end_time=base_time,
        latency_ms=45.0,
        success=True,
    )

    reasoning_trace = inspector.track_reasoning(
        run_id="config_a",
        trace_type="rag_reasoning",
        query="What causes climate change?",
        steps=[step],
        final_answer="Greenhouse gas emissions...",
        reasoning_quality_score=0.93,
        logical_consistency=0.96,
    )

    print(f"✅ Reasoning quality: {reasoning_trace.reasoning_quality_score:.0%}")
    print(f"✅ Logical consistency: {reasoning_trace.logical_consistency:.0%}")

    # ========================================================================
    # 3. WHAT-IF ANALYSIS
    # ========================================================================
    print_header("3. What-If Analysis")

    print("Scenario: What if we reduce context size to save costs?\n")

    scenario = inspector.simulate_scenario(
        run_id="config_a",
        scenario_name="Reduce context for cost savings",
        scenario_type="context",
        original_config={"context_tokens": 2000},
        alternative_config={"context_tokens": 1200},
        original_quality=0.93,
        original_latency_ms=2100.0,
        original_cost_usd=0.015,
        alternative_quality=0.90,
        alternative_latency_ms=1300.0,
        alternative_cost_usd=0.009,
    )

    print(f"📉 Quality change:  {scenario.quality_delta_pct:+.1f}%")
    print(f"📉 Latency change:  {scenario.latency_delta_pct:+.1f}%")
    print(f"📉 Cost change:     {scenario.cost_delta_pct:+.1f}%")
    print(f"\n✅ Recommendation: {scenario.recommendation.upper()}")
    print(f"   {scenario.recommendation_rationale}")

    # ========================================================================
    # 4. COMPARISON
    # ========================================================================
    print_header("4. Comparison & Winner Determination")

    comparator = RAIAComparator(storage)

    comparison = comparator.compare_runs(
        run_ids=["config_a", "config_b"],
        comparison_name="A/B Test: GPT-4 vs GPT-3.5-Turbo"
    )

    print(f"Comparing 2 configurations:\n")
    print(f"{'Configuration':<20} {'Quality':>12} {'Latency':>12} {'Cost':>12}")
    print("-" * 70)

    for run_id in comparison.run_ids:
        name = "GPT-4 (A)" if run_id == "config_a" else "GPT-3.5-Turbo (B)"
        quality = comparison.avg_quality[run_id]
        latency = comparison.avg_latency_ms[run_id]
        cost = comparison.avg_cost_usd[run_id]

        badges = []
        if run_id == comparison.best_quality_run:
            badges.append("👑")
        if run_id == comparison.best_cost_run:
            badges.append("💰")

        badge_str = " ".join(badges)
        print(f"{name:<20} {quality:>11.0%} {latency:>10.0f}ms ${cost:>10.6f} {badge_str}")

    print(f"\n🏆 Overall Winner: {comparison.overall_winner}")
    print(f"   {comparison.winner_rationale}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("SUMMARY")

    print("✅ Tracked metrics for 2 RAG configurations (6 queries total)")
    print("✅ Demonstrated attribution tracking (document → answer mapping)")
    print("✅ Captured reasoning trace (step-by-step process)")
    print("✅ Simulated what-if scenario (cost optimization)")
    print("✅ Compared configurations and determined winner")

    print("\n📊 All data saved to: quickstart_demo.db\n")

    print("=" * 80)
    print("  WHAT'S NEXT?")
    print("=" * 80)

    print("\n1. Run realistic RAG evaluation:")
    print("   python3 examples/realistic_rag_evaluation.py")

    print("\n2. Run complete workflow demo:")
    print("   python3 demo_complete.py")

    print("\n3. Query the database:")
    print("   sqlite3 quickstart_demo.db")

    print("\n4. Read the quick start guide:")
    print("   cat QUICKSTART.md")

    print("\n5. Integrate with your RAG system:")
    print("   from raia import RAIARAGInspector, SQLiteRAIAStorage")
    print("   storage = SQLiteRAIAStorage('my_rag.db')")
    print("   inspector = RAIARAGInspector(storage=storage)")

    print("\n✅ RAIA is production-ready!")
    print("\nTo clean up demo database:")
    print("  rm quickstart_demo.db\n")


if __name__ == "__main__":
    main()
