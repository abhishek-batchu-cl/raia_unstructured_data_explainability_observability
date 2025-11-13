#!/usr/bin/env python3
"""
RAIA What-If Analysis Demo

Demonstrates counterfactual analysis for RAG systems.
Shows how RAIA enables proactive optimization through what-if scenarios.

UNIQUE TO RAIA - No competitor offers this capability!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from raia import (
    RAIARAGInspector,
    SQLiteRAIAStorage,
    RAIAOptimizationRecommendation,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def demo_retrieval_whatif():
    """Demo: What if we retrieved more documents?"""
    print_section("DEMO 1: Retrieval What-If Analysis")

    storage = SQLiteRAIAStorage("demo_whatif.db")
    inspector = RAIARAGInspector(storage=storage)

    run_id = "whatif_run_001"

    print("Scenario: Should we increase retrieval from 5 to 10 documents?")
    print("\nOriginal Configuration:")
    print("  - Retrieved documents: 5")
    print("  - Reranking: Enabled")
    print("  - Quality: 0.89")
    print("  - Latency: 1200ms")
    print("  - Cost: $0.0018")

    print("\nAlternative Configuration:")
    print("  - Retrieved documents: 10")
    print("  - Reranking: Enabled")
    print("  - Estimated quality: 0.91 (+2%)")
    print("  - Estimated latency: 2100ms (+75%)")
    print("  - Estimated cost: $0.0034 (+89%)")

    scenario = inspector.simulate_scenario(
        run_id=run_id,
        scenario_name="Increase retrieval from 5 to 10 documents",
        scenario_type="retrieval",
        original_config={"num_docs": 5, "rerank": True},
        alternative_config={"num_docs": 10, "rerank": True},
        original_quality=0.89,
        original_latency_ms=1200.0,
        original_cost_usd=0.0018,
        alternative_quality=0.91,
        alternative_latency_ms=2100.0,
        alternative_cost_usd=0.0034,
    )

    print_subsection("Analysis Results")
    print(f"Quality Change:    {scenario.quality_delta:+.3f} ({scenario.quality_delta_pct:+.1f}%)")
    print(f"Latency Change:    {scenario.latency_delta_ms:+.0f}ms ({scenario.latency_delta_pct:+.1f}%)")
    print(f"Cost Change:       ${scenario.cost_delta_usd:+.6f} ({scenario.cost_delta_pct:+.1f}%)")
    print(f"\nIs Improvement?    {'✅ Yes' if scenario.is_improvement else '❌ No'}")
    print(f"Recommendation:    {scenario.recommendation.upper()}")
    print(f"Confidence:        {scenario.confidence:.2%}")

    print_subsection("Rationale")
    print(scenario.recommendation_rationale)

    print_subsection("Trade-offs")
    print("Pros:")
    for pro in scenario.pros:
        print(f"  ✅ {pro}")
    print("\nCons:")
    for con in scenario.cons:
        print(f"  ❌ {con}")

    return run_id


def demo_context_whatif():
    """Demo: What if we reduced context size?"""
    print_section("DEMO 2: Context Size What-If Analysis")

    storage = SQLiteRAIAStorage("demo_whatif.db")
    inspector = RAIARAGInspector(storage=storage)

    run_id = "whatif_run_002"

    print("Scenario: Can we reduce context size to save costs?")
    print("\nOriginal Configuration:")
    print("  - Context tokens: 2000")
    print("  - Quality: 0.92")
    print("  - Latency: 1800ms")
    print("  - Cost: $0.0045")

    print("\nAlternative Configuration:")
    print("  - Context tokens: 1200")
    print("  - Estimated quality: 0.91 (-1%)")
    print("  - Estimated latency: 1100ms (-39%)")
    print("  - Estimated cost: $0.0027 (-40%)")

    scenario = inspector.simulate_scenario(
        run_id=run_id,
        scenario_name="Reduce context from 2000 to 1200 tokens",
        scenario_type="context",
        original_config={"context_tokens": 2000},
        alternative_config={"context_tokens": 1200},
        original_quality=0.92,
        original_latency_ms=1800.0,
        original_cost_usd=0.0045,
        alternative_quality=0.91,
        alternative_latency_ms=1100.0,
        alternative_cost_usd=0.0027,
    )

    print_subsection("Analysis Results")
    print(f"Quality Change:    {scenario.quality_delta:+.3f} ({scenario.quality_delta_pct:+.1f}%)")
    print(f"Latency Change:    {scenario.latency_delta_ms:+.0f}ms ({scenario.latency_delta_pct:+.1f}%)")
    print(f"Cost Change:       ${scenario.cost_delta_usd:+.6f} ({scenario.cost_delta_pct:+.1f}%)")
    print(f"\nIs Improvement?    {'✅ Yes' if scenario.is_improvement else '❌ No'}")
    print(f"Recommendation:    {scenario.recommendation.upper()}")
    print(f"Confidence:        {scenario.confidence:.2%}")

    print_subsection("Rationale")
    print(scenario.recommendation_rationale)

    print_subsection("Trade-offs")
    print("Pros:")
    for pro in scenario.pros:
        print(f"  ✅ {pro}")
    print("\nCons:")
    for con in scenario.cons:
        print(f"  ❌ {con}")

    # ROI calculation
    print_subsection("ROI Calculation")
    queries_per_month = 100000
    monthly_savings = scenario.cost_delta_usd * queries_per_month * -1
    annual_savings = monthly_savings * 12
    print(f"Queries per month:     {queries_per_month:,}")
    print(f"Monthly savings:       ${monthly_savings:,.2f}")
    print(f"Annual savings:        ${annual_savings:,.2f}")
    print(f"Quality impact:        Minimal (-1%)")
    print(f"Verdict:               ✅ WORTH IT!")

    return run_id


def demo_cost_optimization():
    """Demo: What if we used a smaller LLM?"""
    print_section("DEMO 3: LLM Selection What-If Analysis")

    storage = SQLiteRAIAStorage("demo_whatif.db")
    inspector = RAIARAGInspector(storage=storage)

    run_id = "whatif_run_003"

    print("Scenario: Should we switch from GPT-4 to GPT-3.5-turbo?")
    print("\nOriginal Configuration:")
    print("  - LLM: GPT-4")
    print("  - Quality: 0.94")
    print("  - Latency: 2200ms")
    print("  - Cost: $0.015")

    print("\nAlternative Configuration:")
    print("  - LLM: GPT-3.5-turbo")
    print("  - Estimated quality: 0.86 (-8.5%)")
    print("  - Estimated latency: 1100ms (-50%)")
    print("  - Estimated cost: $0.002 (-87%)")

    scenario = inspector.simulate_scenario(
        run_id=run_id,
        scenario_name="Switch from GPT-4 to GPT-3.5-turbo",
        scenario_type="cost_optimization",
        original_config={"llm": "gpt-4", "temperature": 0.2},
        alternative_config={"llm": "gpt-3.5-turbo", "temperature": 0.2},
        original_quality=0.94,
        original_latency_ms=2200.0,
        original_cost_usd=0.015,
        alternative_quality=0.86,
        alternative_latency_ms=1100.0,
        alternative_cost_usd=0.002,
    )

    print_subsection("Analysis Results")
    print(f"Quality Change:    {scenario.quality_delta:+.3f} ({scenario.quality_delta_pct:+.1f}%)")
    print(f"Latency Change:    {scenario.latency_delta_ms:+.0f}ms ({scenario.latency_delta_pct:+.1f}%)")
    print(f"Cost Change:       ${scenario.cost_delta_usd:+.6f} ({scenario.cost_delta_pct:+.1f}%)")
    print(f"\nIs Improvement?    {'✅ Yes' if scenario.is_improvement else '❌ No'}")
    print(f"Recommendation:    {scenario.recommendation.upper()}")
    print(f"Confidence:        {scenario.confidence:.2%}")

    print_subsection("Rationale")
    print(scenario.recommendation_rationale)

    print_subsection("Trade-offs")
    print("Pros:")
    for pro in scenario.pros:
        print(f"  ✅ {pro}")
    print("\nCons:")
    for con in scenario.cons:
        print(f"  ❌ {con}")

    # ROI calculation
    print_subsection("ROI Calculation")
    queries_per_month = 50000
    monthly_savings = scenario.cost_delta_usd * queries_per_month * -1
    annual_savings = monthly_savings * 12
    print(f"Queries per month:     {queries_per_month:,}")
    print(f"Monthly savings:       ${monthly_savings:,.2f}")
    print(f"Annual savings:        ${annual_savings:,.2f}")
    print(f"Quality impact:        Significant (-8.5%)")
    print(f"Verdict:               ⚠️  DEPENDS ON USE CASE")
    print(f"Suggestion:            Use GPT-3.5 for simple queries, GPT-4 for complex ones")

    return run_id


def demo_optimization_recommendation():
    """Demo: Generate optimization recommendation."""
    print_section("DEMO 4: Optimization Recommendation")

    storage = SQLiteRAIAStorage("demo_whatif.db")

    run_id = "whatif_run_004"

    print("Based on all what-if analyses, here's our optimization recommendation:")

    recommendation = RAIAOptimizationRecommendation(
        run_id=run_id,
        recommendation_name="Implement smart context sizing + query routing",
        optimization_goal="cost_latency",
        current_quality=0.92,
        current_latency_ms=1800.0,
        current_cost_usd=0.0045,
        recommended_changes={
            "context_strategy": "dynamic_sizing",
            "min_context_tokens": 800,
            "max_context_tokens": 2000,
            "query_router": "enable",
            "simple_queries_llm": "gpt-3.5-turbo",
            "complex_queries_llm": "gpt-4",
            "complexity_threshold": 0.7,
        },
        expected_quality=0.91,
        expected_latency_ms=1250.0,
        expected_cost_usd=0.0028,
        quality_improvement_pct=-1.1,
        latency_improvement_pct=-30.6,
        cost_savings_pct=-37.8,
        implementation_difficulty="medium",
        implementation_steps=[
            "Implement query complexity classifier",
            "Add LLM routing logic based on complexity score",
            "Implement dynamic context sizing based on query type",
            "Add monitoring for quality degradation",
            "Gradual rollout with A/B testing",
        ],
        estimated_implementation_time="1-2 weeks",
        risk_level="low",
        risks=[
            "Quality degradation for edge cases",
            "Complexity classifier accuracy",
            "Increased system complexity",
        ],
        mitigation_strategies=[
            "Thorough testing of complexity classifier",
            "Fallback to GPT-4 for uncertain cases",
            "Continuous quality monitoring with alerts",
            "Easy rollback mechanism",
        ],
        priority="high",
        priority_rationale="High cost savings with minimal quality impact and manageable implementation complexity",
        estimated_annual_savings_usd=78000.0,
        estimated_roi_pct=650.0,
    )

    storage.save_optimization_recommendation(recommendation)

    print_subsection("Recommended Changes")
    for key, value in recommendation.recommended_changes.items():
        print(f"  • {key}: {value}")

    print_subsection("Expected Outcomes")
    print(f"Quality:           {recommendation.current_quality:.2%} → {recommendation.expected_quality:.2%} ({recommendation.quality_improvement_pct:+.1f}%)")
    print(f"Latency:           {recommendation.current_latency_ms:.0f}ms → {recommendation.expected_latency_ms:.0f}ms ({recommendation.latency_improvement_pct:+.1f}%)")
    print(f"Cost:              ${recommendation.current_cost_usd:.6f} → ${recommendation.expected_cost_usd:.6f} ({recommendation.cost_savings_pct:+.1f}%)")

    print_subsection("Implementation Plan")
    print(f"Difficulty:        {recommendation.implementation_difficulty.upper()}")
    print(f"Time estimate:     {recommendation.estimated_implementation_time}")
    print("\nSteps:")
    for i, step in enumerate(recommendation.implementation_steps, 1):
        print(f"  {i}. {step}")

    print_subsection("Risk Assessment")
    print(f"Risk level:        {recommendation.risk_level.upper()}")
    print("\nRisks:")
    for risk in recommendation.risks:
        print(f"  ⚠️  {risk}")
    print("\nMitigation:")
    for mitigation in recommendation.mitigation_strategies:
        print(f"  ✅ {mitigation}")

    print_subsection("ROI Analysis")
    print(f"Annual savings:    ${recommendation.estimated_annual_savings_usd:,.2f}")
    print(f"ROI:               {recommendation.estimated_roi_pct:.0f}%")
    print(f"Priority:          {recommendation.priority.upper()}")
    print(f"\nRationale: {recommendation.priority_rationale}")

    return run_id


def main():
    """Run all what-if analysis demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  RAIA WHAT-IF ANALYSIS DEMO".center(78) + "║")
    print("║" + "  Counterfactual Optimization for RAG Systems".center(78) + "║")
    print("║" + "  UNIQUE TO RAIA - No Competitor Offers This!".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run demos
    run1 = demo_retrieval_whatif()
    run2 = demo_context_whatif()
    run3 = demo_cost_optimization()
    run4 = demo_optimization_recommendation()

    # Summary
    print_section("SUMMARY: Why What-If Analysis Matters")

    print("Traditional Evaluation: Tells you WHAT happened")
    print("  • Quality: 0.89")
    print("  • Latency: 1200ms")
    print("  • Cost: $0.0018")
    print("  ❓ But is this optimal? Can we do better?")

    print("\nRAIA What-If Analysis: Tells you what COULD happen")
    print("  • What if we change retrieval? → -$325k/year possible")
    print("  • What if we change context? → -40% cost, minimal quality impact")
    print("  • What if we change LLM? → -87% cost, but -8.5% quality")
    print("  ✅ Enables data-driven optimization!")

    print("\nBusiness Value:")
    print("  1. 💰 Cost Savings: Identify optimization opportunities")
    print("  2. ⚡ Performance: Balance quality vs latency vs cost")
    print("  3. 🎯 Proactive: Simulate before implementing")
    print("  4. 📊 Data-Driven: Replace gut feelings with analysis")
    print("  5. 🚀 ROI: $78k annual savings from one recommendation!")

    print("\nUnique Differentiators:")
    print("  ✅ Counterfactual scenarios (UNIQUE TO RAIA)")
    print("  ✅ Trade-off analysis with recommendations")
    print("  ✅ ROI calculations for optimizations")
    print("  ✅ Risk assessment and mitigation")
    print("  ✅ Prioritized action plan")

    print(f"\n✅ Demo completed successfully!")
    print(f"✅ Scenarios saved for runs: {run1}, {run2}, {run3}, {run4}")
    print(f"✅ Database: demo_whatif.db\n")

    print("To clean up:")
    print("  rm demo_whatif.db")
    print()


if __name__ == "__main__":
    main()
