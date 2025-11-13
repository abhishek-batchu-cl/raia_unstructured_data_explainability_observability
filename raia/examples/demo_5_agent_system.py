#!/usr/bin/env python3
"""
5-Agent Research System with Complete RAIA Instrumentation

This demo shows a realistic multi-agent system with:
- 5 specialized agents working together
- Both RAIA event logging and behavioral analysis
- All metrics captured and displayed

Agents:
1. Planner - Creates research plan
2. Researcher - Gathers information
3. Analyst - Analyzes data
4. Critic - Reviews quality
5. Reporter - Generates final report
"""

import asyncio
import json
import time
from datetime import datetime
from typing import TypedDict, Annotated, List
from pathlib import Path

# LangGraph imports (we'll create a mock version if not available)
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph not installed. Using mock implementation.")

# RAIA unified library imports
import sys
sys.path.insert(0, '/Users/abhishekbatchu/Documents/raia_agentic_evaluation')

from raia import (
    # Event Logging
    EventEmitter,
    EmitterConfig,
    TransportType,
    # Behavioral Analysis
    RAIAExecutionInspector,
    RAIABehaviorInspector,
    # Storage
    SQLiteRAIAStorage,
)


# ============================================================================
# State Definition
# ============================================================================

class ResearchState(TypedDict):
    """State for the research workflow."""
    query: str
    plan: str
    research_data: List[str]
    analysis: str
    critique: str
    report: str
    iteration_count: int
    node_counts: dict  # For loop detection


# ============================================================================
# Agent Implementations (Simulated)
# ============================================================================

class SimulatedAgent:
    """Simulated agent that mimics LLM behavior with timing."""

    def __init__(self, name: str, base_latency: float = 0.5):
        self.name = name
        self.base_latency = base_latency
        self.call_count = 0

    def invoke(self, input_text: str) -> str:
        """Simulate agent processing."""
        self.call_count += 1
        # Simulate processing time
        time.sleep(self.base_latency)
        return f"[{self.name}] Processed: {input_text[:50]}..."


# ============================================================================
# Node Functions
# ============================================================================

def planner_node(state: ResearchState) -> ResearchState:
    """Agent 1: Creates a research plan."""
    print(f"\n🧠 Agent 1: PLANNER (Iteration {state['iteration_count']})")

    agent = SimulatedAgent("Planner", base_latency=0.3)
    plan = agent.invoke(f"Create research plan for: {state['query']}")

    # Simulate creating a plan
    plan_text = f"""Research Plan for: {state['query']}

    Step 1: Search for recent papers and articles
    Step 2: Gather statistical data
    Step 3: Identify key trends
    Step 4: Compare different approaches
    Step 5: Synthesize findings

    Created at: {datetime.now().isoformat()}
    """

    state["plan"] = plan_text
    state["node_counts"]["planner"] = state["node_counts"].get("planner", 0) + 1

    print(f"   ✓ Plan created ({len(plan_text)} chars)")
    return state


def researcher_node(state: ResearchState) -> ResearchState:
    """Agent 2: Gathers research data."""
    print(f"\n🔍 Agent 2: RESEARCHER (Iteration {state['iteration_count']})")

    agent = SimulatedAgent("Researcher", base_latency=0.8)

    # Simulate multiple research calls
    research_data = []
    sources = ["Academic Papers", "Industry Reports", "News Articles", "Statistics"]

    for source in sources:
        result = agent.invoke(f"Search {source} for: {state['query']}")
        data = f"Data from {source}: Key findings about {state['query']} including metrics, trends, and insights."
        research_data.append(data)
        time.sleep(0.2)  # Simulate tool call latency

    state["research_data"] = research_data
    state["node_counts"]["researcher"] = state["node_counts"].get("researcher", 0) + 1

    print(f"   ✓ Gathered {len(research_data)} sources")
    return state


def analyst_node(state: ResearchState) -> ResearchState:
    """Agent 3: Analyzes the gathered data."""
    print(f"\n📊 Agent 3: ANALYST (Iteration {state['iteration_count']})")

    agent = SimulatedAgent("Analyst", base_latency=0.6)

    # Analyze research data
    analysis_input = f"Analyze: {len(state['research_data'])} sources about {state['query']}"
    result = agent.invoke(analysis_input)

    analysis_text = f"""Analysis Results:

    Sources Analyzed: {len(state['research_data'])}

    Key Findings:
    1. Strong trend towards increased adoption
    2. Multiple competing approaches identified
    3. Cost-benefit analysis shows positive ROI
    4. Implementation challenges documented

    Confidence: High
    Data Quality: Good
    Analysis Date: {datetime.now().isoformat()}
    """

    state["analysis"] = analysis_text
    state["node_counts"]["analyst"] = state["node_counts"].get("analyst", 0) + 1

    print(f"   ✓ Analysis complete ({len(analysis_text)} chars)")
    return state


def critic_node(state: ResearchState) -> ResearchState:
    """Agent 4: Reviews and critiques the work."""
    print(f"\n🎯 Agent 4: CRITIC (Iteration {state['iteration_count']})")

    agent = SimulatedAgent("Critic", base_latency=0.4)

    # Critique the analysis
    critique_input = f"Review analysis quality for: {state['query']}"
    result = agent.invoke(critique_input)

    # Simulate quality check
    quality_score = 0.85 if state["iteration_count"] == 0 else 0.95

    critique_text = f"""Quality Review:

    Completeness: {quality_score * 100:.0f}%
    Accuracy: High
    Sources: Adequate
    Analysis Depth: {'Needs improvement' if quality_score < 0.9 else 'Excellent'}

    Recommendation: {'Iterate and improve' if quality_score < 0.9 else 'Ready for reporting'}
    """

    state["critique"] = critique_text
    state["node_counts"]["critic"] = state["node_counts"].get("critic", 0) + 1

    print(f"   ✓ Critique complete (Quality: {quality_score * 100:.0f}%)")
    return state


def reporter_node(state: ResearchState) -> ResearchState:
    """Agent 5: Generates final report."""
    print(f"\n📝 Agent 5: REPORTER (Iteration {state['iteration_count']})")

    agent = SimulatedAgent("Reporter", base_latency=0.5)

    # Generate report
    report_input = f"Create report from analysis: {state['query']}"
    result = agent.invoke(report_input)

    report_text = f"""
═══════════════════════════════════════════════════════════════════════
                          RESEARCH REPORT
═══════════════════════════════════════════════════════════════════════

Topic: {state['query']}
Generated: {datetime.now().isoformat()}
Iteration: {state['iteration_count'] + 1}

EXECUTIVE SUMMARY
{'-' * 70}
Based on comprehensive research across {len(state['research_data'])} sources,
this report presents key findings and recommendations.

METHODOLOGY
{'-' * 70}
{state['plan'][:200]}...

KEY FINDINGS
{'-' * 70}
{state['analysis'][:300]}...

QUALITY ASSESSMENT
{'-' * 70}
{state['critique'][:200]}...

RECOMMENDATIONS
{'-' * 70}
1. Implement findings in phased approach
2. Monitor key metrics identified
3. Iterate based on results

CONCLUSION
{'-' * 70}
Research completed successfully with high confidence in findings.

═══════════════════════════════════════════════════════════════════════
"""

    state["report"] = report_text
    state["node_counts"]["reporter"] = state["node_counts"].get("reporter", 0) + 1

    print(f"   ✓ Report generated ({len(report_text)} chars)")
    return state


def should_iterate(state: ResearchState) -> str:
    """Decide if we should iterate or finish."""
    # Iterate once to demonstrate loop detection
    if state["iteration_count"] < 1:
        print(f"\n🔄 Quality check: Iterating for improvement (iteration {state['iteration_count']})")
        state["iteration_count"] += 1
        return "iterate"
    else:
        print(f"\n✅ Quality check: Report approved, finishing")
        return "finish"


# ============================================================================
# Main Application
# ============================================================================

async def run_instrumented_demo():
    """Run the 5-agent system with complete RAIA instrumentation."""

    print("=" * 80)
    print("         5-AGENT RESEARCH SYSTEM WITH RAIA INSTRUMENTATION")
    print("=" * 80)
    print()

    # ========================================================================
    # Setup RAIA Event Logging
    # ========================================================================

    print("🔧 Setting up RAIA event logging...")

    emitter_config = EmitterConfig(
        tenant="demo",
        project="5-agent-research",
        agent_id="research-system",
        region="local",
        deployment="dev",
        transport=TransportType.FILE,
        file_path="./data/5_agent_events.jsonl",
        batch_size=10,
        flush_interval_ms=1000,
    )

    emitter = EventEmitter(emitter_config)
    await emitter.start()
    print("   ✓ Event emitter started")

    # ========================================================================
    # Setup RAIA Behavioral Analysis
    # ========================================================================

    print("🔧 Setting up RAIA behavioral analysis...")

    storage = SQLiteRAIAStorage("./data/5_agent_metrics.db")
    exec_inspector = RAIAExecutionInspector(
        storage=storage,
        agent_name="5-agent-research-system",
        graph_name="research-workflow"
    )
    behavior_inspector = RAIABehaviorInspector(
        storage=storage,
        loop_threshold=2,  # Detect if same node runs 2+ times
        redundancy_window=5
    )
    print("   ✓ Inspectors initialized")

    # ========================================================================
    # Initialize State
    # ========================================================================

    initial_state = ResearchState(
        query="Impact of AI agents in enterprise automation",
        plan="",
        research_data=[],
        analysis="",
        critique="",
        report="",
        iteration_count=0,
        node_counts={}
    )

    # ========================================================================
    # Emit Session Start Event
    # ========================================================================

    session_id = exec_inspector.run_id

    emitter.emit({
        "event": "session_start",
        "session_id": session_id,
        "run_id": session_id,
        "agent_id": "research-system",
        "user_id": "demo-user",
        "task": initial_state["query"],
        "domain": "research",
        "graph_name": "5-agent-research-workflow",
    })

    print(f"\n📍 Session started: {session_id}")
    print(f"📍 Query: {initial_state['query']}")
    print()

    # ========================================================================
    # Execute Workflow (Simulated Graph)
    # ========================================================================

    workflow_start = time.time()
    state = initial_state

    # First iteration
    print("\n" + "=" * 80)
    print("                        ITERATION 1")
    print("=" * 80)

    # Execute each node with instrumentation
    for node_name, node_func in [
        ("planner", planner_node),
        ("researcher", researcher_node),
        ("analyst", analyst_node),
        ("critic", critic_node),
        ("reporter", reporter_node),
    ]:
        node_start = time.time()

        # Emit node start event
        emitter.emit({
            "event": "node_start",
            "session_id": session_id,
            "node_name": node_name,
            "iteration": state["iteration_count"],
        })

        # Execute node
        state = node_func(state)

        node_latency = (time.time() - node_start) * 1000

        # Record metrics with inspector
        behavior_inspector.record_node_execution(
            run_id=session_id,
            node_name=node_name,
            state=state,
            latency_ms=node_latency
        )

        # Emit node end event
        emitter.emit({
            "event": "node_end",
            "session_id": session_id,
            "node_name": node_name,
            "latency_ms": node_latency,
            "iteration": state["iteration_count"],
        })

    # Check if should iterate
    decision = should_iterate(state)

    if decision == "iterate":
        print("\n" + "=" * 80)
        print("                        ITERATION 2")
        print("=" * 80)

        # Second iteration (demonstrating loop detection)
        for node_name, node_func in [
            ("planner", planner_node),
            ("researcher", researcher_node),
            ("analyst", analyst_node),
            ("critic", critic_node),
            ("reporter", reporter_node),
        ]:
            node_start = time.time()

            emitter.emit({
                "event": "node_start",
                "session_id": session_id,
                "node_name": node_name,
                "iteration": state["iteration_count"],
            })

            state = node_func(state)

            node_latency = (time.time() - node_start) * 1000

            behavior_inspector.record_node_execution(
                run_id=session_id,
                node_name=node_name,
                state=state,
                latency_ms=node_latency
            )

            emitter.emit({
                "event": "node_end",
                "session_id": session_id,
                "node_name": node_name,
                "latency_ms": node_latency,
                "iteration": state["iteration_count"],
            })

    total_latency = (time.time() - workflow_start) * 1000

    # ========================================================================
    # Finalize and Save Metrics
    # ========================================================================

    print("\n" + "=" * 80)
    print("                    FINALIZING EXECUTION")
    print("=" * 80)

    # Save run summary
    exec_inspector.save_run(
        status="success",
        total_latency_ms=total_latency,
        total_tokens_prompt=250,  # Simulated
        total_tokens_completion=1200,  # Simulated
        total_cost_usd=0.015,  # Simulated
    )

    # Detect patterns
    behavior_inspector.finalize_run(session_id)

    # Emit final event
    emitter.emit({
        "event": "finalized",
        "session_id": session_id,
        "run_id": session_id,
        "agent_id": "research-system",
        "final_answer": state["report"][:200] + "...",
        "success": True,
        "latency_ms": total_latency,
        "total_nodes_executed": sum(state["node_counts"].values()),
    })

    # Flush and shutdown
    await emitter.shutdown()
    print("   ✓ Events flushed and saved")

    # ========================================================================
    # Display All Metrics
    # ========================================================================

    print("\n" + "=" * 80)
    print("                    📊 RAIA METRICS SUMMARY")
    print("=" * 80)

    # Get run data
    run = storage.get_run(session_id)
    node_metrics = storage.get_node_metrics_for_run(session_id)
    signals = storage.get_functional_signals_for_run(session_id)

    print(f"\n{'RUN SUMMARY'}")
    print(f"{'-' * 80}")
    print(f"  Run ID:              {run.run_id}")
    print(f"  Agent Name:          {run.agent_name}")
    print(f"  Graph Name:          {run.graph_name}")
    print(f"  Status:              {run.status}")
    print(f"  Start Time:          {run.start_time}")
    print(f"  End Time:            {run.end_time}")
    print(f"  Total Latency:       {run.total_latency_ms:.2f} ms")
    print(f"  Total Tokens:        {run.total_tokens_prompt + run.total_tokens_completion}")
    print(f"    - Prompt:          {run.total_tokens_prompt}")
    print(f"    - Completion:      {run.total_tokens_completion}")
    print(f"  Estimated Cost:      ${run.total_cost_usd:.4f}")

    print(f"\n{'NODE-LEVEL METRICS'}")
    print(f"{'-' * 80}")
    print(f"  Total Nodes:         {len(node_metrics)}")
    print()

    for metric in sorted(node_metrics, key=lambda x: x.start_time):
        print(f"  📍 {metric.node_name}")
        print(f"     Latency:          {metric.latency_ms:.2f} ms")
        print(f"     Tokens (P/C):     {metric.tokens_prompt}/{metric.tokens_completion}")
        print(f"     Cost:             ${metric.cost_usd:.6f}")
        print(f"     Status:           {metric.status}")
        print()

    print(f"{'BEHAVIORAL SIGNALS'}")
    print(f"{'-' * 80}")
    print(f"  Total Signals:       {len(signals)}")
    print()

    if signals:
        for signal in signals:
            severity_icon = "🔴" if signal.severity == "high" else "🟡" if signal.severity == "medium" else "🟢"
            print(f"  {severity_icon} {signal.signal_type.upper()}")
            print(f"     Severity:         {signal.severity}")
            print(f"     Message:          {signal.message}")
            if signal.details:
                print(f"     Details:          {signal.details}")
            print()
    else:
        print("  ✅ No issues detected - execution was optimal!")

    print(f"{'EXECUTION STATISTICS'}")
    print(f"{'-' * 80}")
    total_nodes = len(node_metrics)
    avg_latency = sum(m.latency_ms for m in node_metrics) / total_nodes if total_nodes > 0 else 0
    total_tokens = sum((m.tokens_prompt or 0) + (m.tokens_completion or 0) for m in node_metrics)

    print(f"  Nodes Executed:      {total_nodes}")
    print(f"  Average Latency:     {avg_latency:.2f} ms")
    print(f"  Total Tokens Used:   {total_tokens}")
    print(f"  Iterations:          {state['iteration_count'] + 1}")
    print(f"  Unique Nodes:        {len(set(m.node_name for m in node_metrics))}")

    print(f"\n{'DATA LOCATIONS'}")
    print(f"{'-' * 80}")
    print(f"  Metrics Database:    ./data/5_agent_metrics.db")
    print(f"  Event Log:           ./data/5_agent_events.jsonl")

    print("\n" + "=" * 80)
    print("                    ✅ DEMO COMPLETE")
    print("=" * 80)
    print()
    print("🎉 Successfully demonstrated:")
    print("   • 5-agent research workflow")
    print("   • RAIA event logging (audit trail)")
    print("   • RAIA behavioral analysis (performance metrics)")
    print("   • Loop detection (2 iterations)")
    print("   • Complete metrics extraction")
    print()
    print("📊 All metrics captured and stored successfully!")
    print()


if __name__ == "__main__":
    # Create data directory
    Path("./data").mkdir(exist_ok=True)

    # Run the demo
    asyncio.run(run_instrumented_demo())
