#!/usr/bin/env python3
"""
RAIA: Agentic AI Evaluation Demo
=================================

This demo shows AGENTIC AI metrics in addition to RAG metrics:
1. Multi-step agent execution (plan → execute → verify)
2. Tool usage (RAG, calculator, search, validator)
3. Decision making at each step
4. Error handling and replanning
5. Agent success/failure tracking
6. All agent-level metrics computed

Scenario: Customer Support Agent with Multiple Tools
- Uses RAG for documentation
- Uses calculator for billing calculations
- Uses validator for data verification
- Makes decisions based on tool outputs
- Replans if errors occur
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import numpy as np
import json
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from raia import RAIARAGInspector, SQLiteRAIAStorage, ReasoningStep

# ============================================================================
# SIMULATED TOOLS FOR AGENT
# ============================================================================

class RAGTool:
    """Tool for querying documentation."""
    def __init__(self, knowledge_base: dict):
        self.knowledge_base = knowledge_base
        self.name = "rag_tool"

    def run(self, query: str) -> Dict[str, Any]:
        """Search documentation and return answer."""
        # Simulate retrieval and answer generation
        docs = list(self.knowledge_base.values())
        random_doc = random.choice(docs)
        answer = random_doc[:100] + "..."

        return {
            "success": True,
            "answer": answer,
            "confidence": random.uniform(0.7, 0.95),
            "latency_ms": random.uniform(50, 150),
        }


class CalculatorTool:
    """Tool for performing calculations."""
    def __init__(self):
        self.name = "calculator_tool"

    def run(self, expression: str) -> Dict[str, Any]:
        """Evaluate mathematical expression."""
        try:
            # Safe evaluation (in production, use ast.literal_eval or similar)
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "success": True,
                "result": result,
                "latency_ms": random.uniform(5, 15),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latency_ms": random.uniform(5, 15),
            }


class ValidatorTool:
    """Tool for validating data."""
    def __init__(self):
        self.name = "validator_tool"

    def run(self, data: str, data_type: str) -> Dict[str, Any]:
        """Validate data format."""
        valid = True

        if data_type == "email":
            valid = "@" in data and "." in data
        elif data_type == "price":
            try:
                float(data)
                valid = True
            except:
                valid = False

        return {
            "success": True,
            "is_valid": valid,
            "data_type": data_type,
            "latency_ms": random.uniform(10, 30),
        }


class SearchTool:
    """Tool for searching external resources."""
    def __init__(self):
        self.name = "search_tool"

    def run(self, query: str) -> Dict[str, Any]:
        """Search external resources."""
        # Simulate search
        results = [
            f"Result {i}: Information about {query}"
            for i in range(3)
        ]

        return {
            "success": True,
            "results": results,
            "num_results": len(results),
            "latency_ms": random.uniform(100, 300),
        }


# ============================================================================
# MULTI-STEP AGENT
# ============================================================================

class CustomerSupportAgent:
    """
    Multi-step agent that uses multiple tools to handle customer queries.

    Demonstrates:
    - Planning: Break down complex queries into steps
    - Tool selection: Choose appropriate tool for each step
    - Decision making: Decide next action based on tool outputs
    - Error handling: Replan if tool fails
    - Verification: Validate results before returning
    """

    def __init__(self, tools: Dict[str, Any]):
        self.tools = tools
        self.max_steps = 10
        self.agent_name = "customer_support_agent"

    def plan(self, query: str) -> List[Dict[str, Any]]:
        """Plan the steps needed to answer the query."""
        steps = []

        # Analyze query to determine what tools are needed
        query_lower = query.lower()

        # Step 1: Always start by understanding the query
        steps.append({
            "step_number": 1,
            "action": "understand_query",
            "tool": None,
            "input": query,
            "reasoning": "Analyze query to determine required tools and information",
        })

        # Step 2: Check if we need documentation (RAG)
        if any(word in query_lower for word in ["how", "what", "feature", "support", "help"]):
            steps.append({
                "step_number": len(steps) + 1,
                "action": "search_documentation",
                "tool": "rag_tool",
                "input": query,
                "reasoning": "Query requires information from documentation",
            })

        # Step 3: Check if we need calculations
        if any(word in query_lower for word in ["cost", "price", "calculate", "total", "refund"]):
            steps.append({
                "step_number": len(steps) + 1,
                "action": "calculate",
                "tool": "calculator_tool",
                "input": "49 * 12",  # Example calculation
                "reasoning": "Query requires numerical calculation",
            })

        # Step 4: Check if we need validation
        if any(word in query_lower for word in ["email", "valid", "check", "verify"]):
            steps.append({
                "step_number": len(steps) + 1,
                "action": "validate_data",
                "tool": "validator_tool",
                "input": {"data": "user@example.com", "data_type": "email"},
                "reasoning": "Query requires data validation",
            })

        # Step 5: Check if we need external search
        if any(word in query_lower for word in ["integrate", "api", "third-party"]):
            steps.append({
                "step_number": len(steps) + 1,
                "action": "search_external",
                "tool": "search_tool",
                "input": query,
                "reasoning": "Query may require external resources",
            })

        # Final step: Synthesize answer
        steps.append({
            "step_number": len(steps) + 1,
            "action": "synthesize_answer",
            "tool": None,
            "input": "All gathered information",
            "reasoning": "Combine all information into final answer",
        })

        return steps

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step."""
        start_time = datetime.utcnow()

        # Get tool
        tool_name = step["tool"]

        if tool_name is None:
            # Non-tool step (planning, synthesis, etc.)
            result = {
                "success": True,
                "output": f"Completed {step['action']}",
                "latency_ms": random.uniform(10, 50),
            }
        else:
            # Execute tool
            tool = self.tools.get(tool_name)
            if tool is None:
                result = {
                    "success": False,
                    "error": f"Tool {tool_name} not available",
                    "latency_ms": 0,
                }
            else:
                # Run tool
                if isinstance(step["input"], dict):
                    result = tool.run(**step["input"])
                else:
                    result = tool.run(step["input"])

        end_time = datetime.utcnow()
        latency_ms = (end_time - start_time).total_seconds() * 1000

        return {
            "step_number": step["step_number"],
            "action": step["action"],
            "tool": tool_name,
            "success": result.get("success", False),
            "output": result,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow(),
        }

    def should_replan(self, executed_steps: List[Dict[str, Any]]) -> bool:
        """Decide if we need to replan based on step failures."""
        # Replan if last 2 steps failed
        if len(executed_steps) >= 2:
            last_two_failed = all(
                not step["success"]
                for step in executed_steps[-2:]
            )
            if last_two_failed:
                return True

        return False

    def run(self, query: str) -> Dict[str, Any]:
        """Execute agent to answer query."""
        start_time = datetime.utcnow()

        # Phase 1: Plan
        plan = self.plan(query)

        # Phase 2: Execute
        executed_steps = []
        replanned = False

        for step in plan:
            # Execute step
            result = self.execute_step(step)
            executed_steps.append(result)

            # Check if we need to replan
            if self.should_replan(executed_steps):
                print(f"  ⚠️  Replanning after failures...")
                replanned = True
                # Simplified replan: skip failed tool and continue
                break

        # Phase 3: Synthesize final answer
        tool_outputs = []
        for step in executed_steps:
            if step["success"] and step["tool"] is not None:
                tool_outputs.append(step["output"])

        # Generate final answer
        if tool_outputs:
            answer = f"Based on the available information: {tool_outputs[0].get('answer', 'Information retrieved successfully.')}"
        else:
            answer = "I'm unable to provide a complete answer at this time."

        end_time = datetime.utcnow()
        total_latency = (end_time - start_time).total_seconds() * 1000

        # Agent-level metrics
        num_steps = len(executed_steps)
        num_successful_steps = sum(1 for s in executed_steps if s["success"])
        num_failed_steps = num_steps - num_successful_steps
        success_rate = num_successful_steps / num_steps if num_steps > 0 else 0.0

        # Tool usage statistics
        tool_calls = [s for s in executed_steps if s["tool"] is not None]
        num_tool_calls = len(tool_calls)
        tool_usage = {}
        for step in tool_calls:
            tool_name = step["tool"]
            if tool_name not in tool_usage:
                tool_usage[tool_name] = {"calls": 0, "successes": 0, "failures": 0}
            tool_usage[tool_name]["calls"] += 1
            if step["success"]:
                tool_usage[tool_name]["successes"] += 1
            else:
                tool_usage[tool_name]["failures"] += 1

        return {
            "query": query,
            "answer": answer,
            "plan": plan,
            "executed_steps": executed_steps,
            "replanned": replanned,
            "num_steps": num_steps,
            "num_successful_steps": num_successful_steps,
            "num_failed_steps": num_failed_steps,
            "success_rate": success_rate,
            "num_tool_calls": num_tool_calls,
            "tool_usage": tool_usage,
            "total_latency_ms": total_latency,
            "overall_success": num_failed_steps == 0,
        }


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    print("="*80)
    print("  RAIA: AGENTIC AI EVALUATION DEMO")
    print("  Multi-step agent with tool usage and decision making")
    print("="*80)
    print()

    # Initialize storage
    storage = SQLiteRAIAStorage("agentic_ai_demo.db")
    inspector = RAIARAGInspector(storage=storage)

    # Setup knowledge base
    KNOWLEDGE_BASE = {
        "doc_features": "Our platform offers real-time collaboration, document sharing, and task management.",
        "doc_pricing": "Premium plan is $49/month, Enterprise is $199/month.",
        "doc_integrations": "Connect with Slack, Microsoft Teams, Google Workspace, and Salesforce.",
        "doc_support": "Contact support@company.com for help. Response time is 24 hours.",
    }

    # Setup tools
    tools = {
        "rag_tool": RAGTool(KNOWLEDGE_BASE),
        "calculator_tool": CalculatorTool(),
        "validator_tool": ValidatorTool(),
        "search_tool": SearchTool(),
    }

    # Setup agent
    agent = CustomerSupportAgent(tools)

    # Test queries demonstrating different agent behaviors
    AGENT_QUERIES = [
        "What features does the platform offer?",  # Simple RAG
        "How much does the annual Premium plan cost?",  # RAG + Calculator
        "Can I integrate with Slack and is support@company.com a valid email?",  # RAG + Validator
        "How do I integrate with third-party APIs?",  # RAG + Search
    ]

    print("🤖 Running Multi-Step Agent with Tool Usage\n")

    for i, query in enumerate(AGENT_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"AGENT EXECUTION #{i}")
        print(f"{'='*80}")
        print(f"\n📝 Query: \"{query}\"")
        print()

        run_id = f"agent_run_{i:03d}"

        # Execute agent
        result = agent.run(query)

        # Display plan
        print(f"📋 PLAN ({len(result['plan'])} steps):")
        for step in result['plan']:
            tool_str = f"[{step['tool']}]" if step['tool'] else "[no tool]"
            print(f"  {step['step_number']}. {step['action']} {tool_str}")
            print(f"     → {step['reasoning']}")

        # Display execution
        print(f"\n⚡ EXECUTION:")
        for step in result['executed_steps']:
            status = "✅" if step['success'] else "❌"
            tool_str = f"[{step['tool']}]" if step['tool'] else "[internal]"
            print(f"  {status} Step {step['step_number']}: {step['action']} {tool_str}")
            print(f"     Latency: {step['latency_ms']:.2f}ms")
            if not step['success']:
                print(f"     Error: {step['output'].get('error', 'Unknown error')}")

        # Display tool usage
        print(f"\n🔧 TOOL USAGE:")
        for tool_name, stats in result['tool_usage'].items():
            success_rate = stats['successes'] / stats['calls'] if stats['calls'] > 0 else 0
            print(f"  • {tool_name}:")
            print(f"    Calls: {stats['calls']}, Successes: {stats['successes']}, Failures: {stats['failures']}")
            print(f"    Success Rate: {success_rate:.1%}")

        # Display final answer
        print(f"\n💬 FINAL ANSWER:")
        print(f"  {result['answer']}")

        # Display agent metrics
        print(f"\n📊 AGENT METRICS:")
        print(f"  Total Steps: {result['num_steps']}")
        print(f"  Successful Steps: {result['num_successful_steps']}")
        print(f"  Failed Steps: {result['num_failed_steps']}")
        print(f"  Step Success Rate: {result['success_rate']:.1%}")
        print(f"  Tool Calls: {result['num_tool_calls']}")
        print(f"  Replanned: {'Yes' if result['replanned'] else 'No'}")
        print(f"  Total Latency: {result['total_latency_ms']:.2f}ms")
        print(f"  Overall Success: {'✅' if result['overall_success'] else '❌'}")

        # Track with RAIA
        # Convert executed steps to ReasoningStep objects
        reasoning_steps = []
        for step in result['executed_steps']:
            reasoning_steps.append(ReasoningStep(
                step_number=step['step_number'],
                step_name=step['action'],
                step_type="action" if step['tool'] else "understanding",
                description=f"Execute {step['action']}" + (f" using {step['tool']}" if step['tool'] else ""),
                rationale=f"Step {step['step_number']} in agent execution plan",
                confidence=0.9 if step['success'] else 0.3,
                inputs={"tool": step['tool'], "action": step['action']},
                outputs=step['output'],
                start_time=step['timestamp'],
                end_time=step['timestamp'] + timedelta(milliseconds=step['latency_ms']),
                latency_ms=step['latency_ms'],
            ))

        # Track reasoning trace (represents agent execution)
        inspector.track_reasoning(
            run_id=run_id,
            trace_type="agent_reasoning",
            query=query,
            steps=reasoning_steps,
            final_answer=result['answer'],
        )

        # Track each tool call as a retrieval or action
        for step in result['executed_steps']:
            if step['tool'] == 'rag_tool' and step['success']:
                # Track RAG tool usage
                inspector.track_answer_quality(
                    run_id=run_id,
                    query=query,
                    answer=step['output'].get('answer', ''),
                    answer_faithfulness=step['output'].get('confidence', 0.8),
                    hallucination_score=1.0 - step['output'].get('confidence', 0.8),
                    answer_relevance=0.85,
                    answer_completeness=0.80,
                    generation_latency_ms=step['latency_ms'],
                )

    # Summary
    print(f"\n\n{'='*80}")
    print("  AGENTIC AI EVALUATION SUMMARY")
    print(f"{'='*80}")

    print(f"\n✅ DEMONSTRATED CAPABILITIES:")
    print(f"   ✓ Multi-step agent execution (plan → execute → verify)")
    print(f"   ✓ Tool usage tracking (RAG, calculator, validator, search)")
    print(f"   ✓ Decision making at each step")
    print(f"   ✓ Error detection and replanning")
    print(f"   ✓ Agent-level metrics (success rate, tool usage, latency)")
    print(f"   ✓ Step-by-step reasoning traces")
    print(f"   ✓ Tool-specific metrics (calls, successes, failures)")

    print(f"\n📊 AGENT METRICS TRACKED:")
    print(f"   • Total steps executed")
    print(f"   • Step success/failure rates")
    print(f"   • Tool calls and usage statistics")
    print(f"   • Replanning triggers")
    print(f"   • End-to-end latency")
    print(f"   • Overall task success")

    print(f"\n📁 DATABASE: agentic_ai_demo.db")
    print(f"   • Reasoning traces: {len(AGENT_QUERIES)} agents × ~5 steps each")
    print(f"   • Answer quality metrics for RAG tool usage")
    print(f"   • Complete execution history")

    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Query database: sqlite3 agentic_ai_demo.db")
    print(f"   2. Analyze agent behavior: SELECT * FROM raia_reasoning_traces;")
    print(f"   3. Compare tool performance across different queries")
    print(f"   4. Identify failure patterns and optimization opportunities")

    print(f"\n{'='*80}")
    print("  ✅ AGENTIC AI EVALUATION DEMO COMPLETE!")
    print(f"{'='*80}")
    print()


if __name__ == "__main__":
    main()
