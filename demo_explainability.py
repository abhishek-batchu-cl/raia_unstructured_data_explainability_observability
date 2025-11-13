#!/usr/bin/env python3
"""
RAIA Explainability Demo

Demonstrates attribution tracking and reasoning traces for RAG systems.
Shows how RAIA provides explainability similar to SHAP/LIME but for
dynamic RAG processes instead of static predictions.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from raia import (
    RAIARAGInspector,
    SQLiteRAIAStorage,
    Attribution,
    ReasoningStep,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def demo_attribution_tracking():
    """
    Demo: Attribution Tracking (Like SHAP for RAG)

    Shows which parts of the answer came from which source documents,
    with confidence scores and hallucination detection.
    """
    print_section("DEMO 1: Attribution Tracking (Document Explainability)")

    # Initialize storage and inspector
    storage = SQLiteRAIAStorage("demo_explainability.db")
    inspector = RAIARAGInspector(storage=storage)

    # Simulated RAG scenario
    run_id = "explain_run_001"
    query = "What are the main causes of climate change?"

    # Simulated answer
    answer = (
        "Climate change is primarily caused by greenhouse gas emissions from fossil fuels, "
        "including coal, oil, and natural gas. Deforestation also contributes significantly "
        "by reducing the planet's capacity to absorb CO2. Industrial processes and "
        "agricultural activities release additional greenhouse gases like methane and nitrous oxide."
    )

    # Simulated source documents
    doc1_id = "ipcc_report_2023"
    doc1_content = "Greenhouse gas emissions from fossil fuels (coal, oil, natural gas) are the primary driver of climate change."

    doc2_id = "nature_deforestation_2022"
    doc2_content = "Deforestation reduces Earth's capacity to absorb carbon dioxide, exacerbating climate change."

    doc3_id = "epa_ghg_sources_2023"
    doc3_content = "Industrial processes and agricultural activities emit greenhouse gases including methane (CH4) and nitrous oxide (N2O)."

    print(f"Query: \"{query}\"\n")
    print(f"Generated Answer:\n\"{answer}\"\n")

    print_subsection("Source Documents")
    print(f"[{doc1_id}]: {doc1_content}")
    print(f"[{doc2_id}]: {doc2_content}")
    print(f"[{doc3_id}]: {doc3_content}")

    # Create attribution mappings
    attributions = [
        Attribution(
            answer_span="greenhouse gas emissions from fossil fuels",
            answer_start_idx=36,
            answer_end_idx=79,
            source_doc_id=doc1_id,
            source_span="Greenhouse gas emissions from fossil fuels",
            source_start_idx=0,
            source_end_idx=42,
            confidence=0.96,
            similarity_score=0.94,
        ),
        Attribution(
            answer_span="including coal, oil, and natural gas",
            answer_start_idx=81,
            answer_end_idx=117,
            source_doc_id=doc1_id,
            source_span="(coal, oil, natural gas)",
            source_start_idx=43,
            source_end_idx=67,
            confidence=0.98,
            similarity_score=0.97,
        ),
        Attribution(
            answer_span="Deforestation also contributes significantly",
            answer_start_idx=119,
            answer_end_idx=163,
            source_doc_id=doc2_id,
            source_span="Deforestation reduces Earth's capacity",
            source_start_idx=0,
            source_end_idx=38,
            confidence=0.92,
            similarity_score=0.89,
        ),
        Attribution(
            answer_span="reducing the planet's capacity to absorb CO2",
            answer_start_idx=167,
            answer_end_idx=211,
            source_doc_id=doc2_id,
            source_span="reduces Earth's capacity to absorb carbon dioxide",
            source_start_idx=14,
            source_end_idx=64,
            confidence=0.95,
            similarity_score=0.93,
        ),
        Attribution(
            answer_span="Industrial processes and agricultural activities",
            answer_start_idx=213,
            answer_end_idx=261,
            source_doc_id=doc3_id,
            source_span="Industrial processes and agricultural activities",
            source_start_idx=0,
            source_end_idx=48,
            confidence=0.99,
            similarity_score=0.99,
        ),
        Attribution(
            answer_span="methane and nitrous oxide",
            answer_start_idx=302,
            answer_end_idx=327,
            source_doc_id=doc3_id,
            source_span="methane (CH4) and nitrous oxide (N2O)",
            source_start_idx=77,
            source_end_idx=115,
            confidence=0.97,
            similarity_score=0.95,
        ),
    ]

    # Track attribution
    attribution_map = inspector.track_attribution(
        run_id=run_id,
        query=query,
        answer=answer,
        attributions=attributions,
        overall_confidence=0.96,
        faithfulness_score=0.98,
        hallucination_score=0.02,
        total_context_tokens=450,
        utilized_context_tokens=385,
        metadata={"model": "gpt-4", "temperature": 0.2},
    )

    print_subsection("Attribution Analysis Results")
    print(f"Overall Confidence:    {attribution_map.overall_confidence:.2%}")
    print(f"Faithfulness Score:    {attribution_map.faithfulness_score:.2%}")
    print(f"Hallucination Score:   {attribution_map.hallucination_score:.2%}")
    print(f"Context Efficiency:    {attribution_map.context_efficiency:.2%}")
    print(f"Unique Sources Used:   {attribution_map.unique_sources_used}")
    print(f"Primary Source:        {attribution_map.primary_source}")

    print_subsection("Attribution Mappings (Answer Span → Source Document)")
    for i, attr in enumerate(attributions, 1):
        print(f"\n{i}. \"{attr.answer_span}\"")
        print(f"   ← [{attr.source_doc_id}] \"{attr.source_span}\"")
        print(f"   Confidence: {attr.confidence:.2%}, Similarity: {attr.similarity_score:.2%}")

    print_subsection("Key Insights")
    print(f"✅ High faithfulness ({attribution_map.faithfulness_score:.2%}) - Answer is well-grounded in sources")
    print(f"✅ Low hallucination ({attribution_map.hallucination_score:.2%}) - Minimal made-up content")
    print(f"✅ Good context efficiency ({attribution_map.context_efficiency:.2%}) - Used most of retrieved context")
    print(f"✅ Multiple sources ({attribution_map.unique_sources_used}) - Diverse information synthesis")

    return run_id


def demo_reasoning_trace():
    """
    Demo: Reasoning Trace (Like LIME for Agents)

    Shows step-by-step how the RAG system reasoned from query to answer,
    with timing, confidence, and bottleneck identification.
    """
    print_section("DEMO 2: Reasoning Trace (Process Explainability)")

    # Initialize storage and inspector
    storage = SQLiteRAIAStorage("demo_explainability.db")
    inspector = RAIARAGInspector(storage=storage)

    # Simulated RAG scenario
    run_id = "explain_run_002"
    query = "What are the main causes of climate change?"

    print(f"Query: \"{query}\"\n")

    # Create reasoning steps
    base_time = datetime.utcnow()

    steps = [
        ReasoningStep(
            step_number=1,
            step_name="Query Understanding",
            step_type="understanding",
            description="Analyzed user query to extract intent and key concepts",
            action_taken="extract_intent(query)",
            rationale="Need to understand query intent before retrieval",
            confidence=0.94,
            inputs={"query": query},
            outputs={
                "intent": "causal_inquiry",
                "key_concepts": ["climate change", "causes", "main factors"],
                "query_type": "factual"
            },
            start_time=base_time,
            end_time=base_time + timedelta(milliseconds=48),
            latency_ms=48.0,
            success=True,
        ),
        ReasoningStep(
            step_number=2,
            step_name="Query Embedding",
            step_type="retrieval",
            description="Generated embedding vector for semantic search",
            action_taken="embed_query(query)",
            rationale="Convert query to vector for similarity search",
            confidence=0.99,
            inputs={"query": query, "model": "text-embedding-ada-002"},
            outputs={
                "embedding_dim": 1536,
                "tokens_used": 9,
                "embedding_cost_usd": 0.000001
            },
            start_time=base_time + timedelta(milliseconds=48),
            end_time=base_time + timedelta(milliseconds=183),
            latency_ms=135.0,
            success=True,
        ),
        ReasoningStep(
            step_number=3,
            step_name="Vector Search",
            step_type="retrieval",
            description="Retrieved top-5 most relevant documents from vector database",
            action_taken="vector_search(embedding, k=5)",
            rationale="Find most semantically similar documents",
            confidence=0.88,
            inputs={"k": 5, "index_name": "climate_docs", "similarity_metric": "cosine"},
            outputs={
                "num_docs_retrieved": 5,
                "avg_similarity": 0.86,
                "search_latency_ms": 42.0,
                "docs_returned": [
                    "ipcc_report_2023",
                    "nature_deforestation_2022",
                    "epa_ghg_sources_2023",
                    "nasa_climate_data_2023",
                    "unfccc_emissions_2022"
                ]
            },
            start_time=base_time + timedelta(milliseconds=183),
            end_time=base_time + timedelta(milliseconds=225),
            latency_ms=42.0,
            success=True,
        ),
        ReasoningStep(
            step_number=4,
            step_name="Document Reranking",
            step_type="retrieval",
            description="Reranked documents using cross-encoder for better relevance",
            action_taken="rerank_documents(query, docs)",
            rationale="Improve precision by reranking with more expensive model",
            confidence=0.91,
            inputs={
                "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                "num_docs": 5
            },
            outputs={
                "reranked_docs": [
                    "ipcc_report_2023",
                    "epa_ghg_sources_2023",
                    "nature_deforestation_2022",
                    "unfccc_emissions_2022",
                    "nasa_climate_data_2023"
                ],
                "top3_scores": [0.94, 0.89, 0.87]
            },
            start_time=base_time + timedelta(milliseconds=225),
            end_time=base_time + timedelta(milliseconds=312),
            latency_ms=87.0,
            success=True,
        ),
        ReasoningStep(
            step_number=5,
            step_name="Context Synthesis",
            step_type="synthesis",
            description="Extracted key facts from top-3 documents and organized by relevance",
            action_taken="synthesize_context(docs)",
            rationale="Prepare concise context for LLM generation",
            confidence=0.90,
            inputs={"num_docs_used": 3, "max_tokens": 500},
            outputs={
                "synthesized_context_tokens": 385,
                "num_facts_extracted": 8,
                "context_quality_score": 0.92
            },
            start_time=base_time + timedelta(milliseconds=312),
            end_time=base_time + timedelta(milliseconds=375),
            latency_ms=63.0,
            success=True,
        ),
        ReasoningStep(
            step_number=6,
            step_name="Answer Generation",
            step_type="generation",
            description="Generated answer using LLM with retrieved context",
            action_taken="generate_answer(query, context)",
            rationale="Synthesize final answer from context",
            confidence=0.96,
            inputs={
                "model": "gpt-4",
                "temperature": 0.2,
                "max_tokens": 200,
                "prompt_tokens": 442,
            },
            outputs={
                "completion_tokens": 87,
                "total_tokens": 529,
                "cost_usd": 0.01587,
                "answer_length": 329
            },
            start_time=base_time + timedelta(milliseconds=375),
            end_time=base_time + timedelta(milliseconds=1842),
            latency_ms=1467.0,
            success=True,
        ),
        ReasoningStep(
            step_number=7,
            step_name="Answer Validation",
            step_type="validation",
            description="Validated answer faithfulness and detected hallucinations",
            action_taken="validate_answer(answer, context)",
            rationale="Ensure answer is grounded in retrieved context",
            confidence=0.98,
            inputs={"answer": "...", "context": "..."},
            outputs={
                "faithfulness_score": 0.98,
                "hallucination_score": 0.02,
                "attribution_quality": 0.96,
                "validation_passed": True
            },
            start_time=base_time + timedelta(milliseconds=1842),
            end_time=base_time + timedelta(milliseconds=1950),
            latency_ms=108.0,
            success=True,
        ),
    ]

    # Track reasoning
    reasoning_trace = inspector.track_reasoning(
        run_id=run_id,
        trace_type="rag_reasoning",
        query=query,
        steps=steps,
        final_answer="Climate change is primarily caused by greenhouse gas emissions...",
        reasoning_quality_score=0.94,
        logical_consistency=0.97,
        metadata={"pipeline_version": "v2.3.1"},
    )

    print_subsection("Reasoning Chain Overview")
    print(f"Total Steps:           {reasoning_trace.total_steps}")
    print(f"Successful Steps:      {reasoning_trace.successful_steps}")
    print(f"Failed Steps:          {reasoning_trace.failed_steps}")
    print(f"Total Latency:         {reasoning_trace.total_latency_ms:.0f}ms")
    print(f"Bottleneck Step:       {reasoning_trace.bottleneck_step}")
    print(f"Reasoning Quality:     {reasoning_trace.reasoning_quality_score:.2%}")
    print(f"Logical Consistency:   {reasoning_trace.logical_consistency:.2%}")

    print_subsection("Step-by-Step Reasoning Process")
    for step in steps:
        status_emoji = "✅" if step.success else "❌"
        print(f"\n{status_emoji} Step {step.step_number}: {step.step_name} ({step.step_type})")
        print(f"   Description: {step.description}")
        print(f"   Confidence: {step.confidence:.2%}, Latency: {step.latency_ms:.0f}ms")
        if step.action_taken:
            print(f"   Action: {step.action_taken}")

        # Show key outputs
        if step.outputs:
            print(f"   Key outputs: {', '.join(f'{k}={v}' for k, v in list(step.outputs.items())[:3])}")

    print_subsection("Performance Breakdown")
    total_latency = reasoning_trace.total_latency_ms
    for step in steps:
        percentage = (step.latency_ms / total_latency) * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        print(f"{step.step_name:25} {step.latency_ms:6.0f}ms [{bar:50}] {percentage:5.1f}%")

    print_subsection("Key Insights")
    print(f"✅ High reasoning quality ({reasoning_trace.reasoning_quality_score:.2%}) - Solid reasoning process")
    print(f"✅ High logical consistency ({reasoning_trace.logical_consistency:.2%}) - All steps successful")
    print(f"⚠️  Bottleneck: {reasoning_trace.bottleneck_step} (75% of total time)")
    print(f"💡 Optimization: Consider using faster LLM or implementing caching")

    return run_id


def demo_explainability_comparison():
    """
    Demo: Compare Traditional ML Explainability vs RAIA

    Shows the conceptual difference between SHAP/LIME and RAIA.
    """
    print_section("DEMO 3: Traditional ML vs RAIA Explainability")

    print_subsection("Traditional ML Explainability (SHAP/LIME)")
    print("Scenario: Credit Scoring Model")
    print("\nInput Features:")
    print("  - age: 35")
    print("  - income: $50,000")
    print("  - credit_score: 720")
    print("  - debt_ratio: 0.3")
    print("\nSHAP Explanation:")
    print("  Prediction: APPROVED (confidence: 0.85)")
    print("  Feature Importance:")
    print("    income (+$50k):      +0.30 ✅")
    print("    credit_score (720):  +0.25 ✅")
    print("    age (35):            +0.15 ✅")
    print("    debt_ratio (0.3):    +0.10 ✅")
    print("\n❌ Problem: Only explains static predictions, not dynamic processes")

    print_subsection("RAIA Explainability (Attribution + Reasoning)")
    print("Scenario: RAG Question Answering")
    print("\nInput Query: \"What causes climate change?\"")
    print("\nRAIA Attribution Explanation:")
    print("  Answer: \"Climate change is caused by greenhouse gas emissions...\"")
    print("  Document Attribution:")
    print("    \"greenhouse gases\"     ← ipcc_report_2023 (0.95) ✅")
    print("    \"fossil fuels\"         ← energy_report_2023 (0.92) ✅")
    print("    \"deforestation\"        ← nature_study_2022 (0.88) ✅")
    print("\nRAIA Reasoning Trace:")
    print("  Step 1: Query Understanding (48ms, confidence: 0.94)")
    print("  Step 2: Query Embedding (135ms, confidence: 0.99)")
    print("  Step 3: Vector Search (42ms, confidence: 0.88)")
    print("  Step 4: Document Reranking (87ms, confidence: 0.91)")
    print("  Step 5: Context Synthesis (63ms, confidence: 0.90)")
    print("  Step 6: Answer Generation (1467ms, confidence: 0.96)")
    print("  Step 7: Answer Validation (108ms, confidence: 0.98)")
    print("\n✅ Advantage: Explains both WHAT (attribution) and HOW (reasoning)")

    print_subsection("Key Differences")
    differences = [
        ("What it explains", "Static predictions", "Dynamic processes"),
        ("Feature Attribution", "✅ Feature importance", "✅ Document attribution"),
        ("Reasoning Traces", "❌ Not applicable", "✅ Step-by-step process"),
        ("Temporal Analysis", "❌ Single point in time", "✅ Multi-step chains"),
        ("Action Explanation", "❌ Not applicable", "✅ Tool/action selection"),
        ("What-If Analysis", "✅ Feature perturbation", "✅ Component scenarios"),
    ]

    print(f"\n{'Capability':<25} {'Traditional ML':<25} {'RAIA (RAG/Agent)':<25}")
    print("-" * 80)
    for capability, traditional, raia in differences:
        print(f"{capability:<25} {traditional:<25} {raia:<25}")


def main():
    """Run all explainability demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  RAIA EXPLAINABILITY DEMO".center(78) + "║")
    print("║" + "  Attribution Tracking + Reasoning Traces for RAG/Agent Systems".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run demos
    run1 = demo_attribution_tracking()
    run2 = demo_reasoning_trace()
    demo_explainability_comparison()

    # Summary
    print_section("SUMMARY: RAIA Explainability Value Proposition")

    print("RAIA provides comprehensive explainability for RAG and Agentic AI systems:")
    print("\n1. ATTRIBUTION TRACKING (Like SHAP for RAG)")
    print("   - Shows which documents contributed to which answer parts")
    print("   - Detects hallucinations and measures faithfulness")
    print("   - Tracks context utilization efficiency")
    print("   - Enables transparency and trust")

    print("\n2. REASONING TRACES (Like LIME for Agents)")
    print("   - Captures step-by-step reasoning process")
    print("   - Identifies bottlenecks and optimization opportunities")
    print("   - Validates logical consistency")
    print("   - Enables debugging and auditing")

    print("\n3. UNIQUE DIFFERENTIATORS")
    print("   - ✅ Dynamic process explanation (not just static predictions)")
    print("   - ✅ Multi-component system analysis")
    print("   - ✅ Temporal reasoning chains")
    print("   - ✅ Complete audit trail for compliance")

    print("\n4. BUSINESS VALUE")
    print("   - 🔍 Debugging: \"Why did my system fail?\"")
    print("   - 🔒 Trust: \"Can I trust this answer?\"")
    print("   - 💰 Optimization: \"How can I reduce costs?\"")
    print("   - 📋 Compliance: \"Prove this decision used approved sources\"")

    print(f"\n✅ Demo completed successfully!")
    print(f"✅ Attribution data saved for run: {run1}")
    print(f"✅ Reasoning trace saved for run: {run2}")
    print(f"✅ Database: demo_explainability.db\n")

    # Cleanup instructions
    print("To view the data:")
    print("  python3 -c \"from raia import SQLiteRAIAStorage; s = SQLiteRAIAStorage('demo_explainability.db'); print(s.get_attribution_maps_for_run('explain_run_001'))\"")
    print("\nTo clean up:")
    print("  rm demo_explainability.db")
    print()


if __name__ == "__main__":
    main()
