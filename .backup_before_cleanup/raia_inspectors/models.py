"""
RAIA Inspectors - Data Models

Pydantic models for capturing agent execution metrics, behavioral signals, and semantic scores.
"""

from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class RAIAAgentRun(BaseModel):
    """
    Represents a complete agent execution run with aggregate metrics.
    """
    run_id: str = Field(..., description="Unique identifier for this run")
    session_id: Optional[str] = Field(None, description="Session ID grouping multiple runs")
    agent_name: Optional[str] = Field(None, description="Name of the agent")
    graph_name: Optional[str] = Field(None, description="Name of the LangGraph graph")
    start_time: datetime = Field(..., description="When the run started")
    end_time: Optional[datetime] = Field(None, description="When the run ended")
    status: Literal["success", "error", "in_progress"] = Field("in_progress", description="Run status")
    total_latency_ms: Optional[float] = Field(None, description="Total execution time in milliseconds")
    total_tokens_prompt: Optional[int] = Field(None, description="Total prompt tokens used")
    total_tokens_completion: Optional[int] = Field(None, description="Total completion tokens used")
    total_cost_usd: Optional[float] = Field(None, description="Estimated total cost in USD")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "session_id": "session_xyz",
                "agent_name": "medical_research_agent",
                "graph_name": "react_graph",
                "start_time": "2024-01-15T10:30:00Z",
                "end_time": "2024-01-15T10:30:45Z",
                "status": "success",
                "total_latency_ms": 45000.0,
                "total_tokens_prompt": 1200,
                "total_tokens_completion": 800,
                "total_cost_usd": 0.0245,
                "metadata": {"environment": "production", "tenant": "acme"}
            }
        }


class RAIANodeMetrics(BaseModel):
    """
    Metrics for a single node/step in the agent execution.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: str = Field(..., description="Name of the node/step")
    node_type: Literal["llm", "tool", "chain", "custom"] = Field(..., description="Type of node")
    start_time: datetime = Field(..., description="When the node started")
    end_time: datetime = Field(..., description="When the node ended")
    latency_ms: float = Field(..., description="Execution time in milliseconds")
    tokens_prompt: Optional[int] = Field(None, description="Prompt tokens for this node")
    tokens_completion: Optional[int] = Field(None, description="Completion tokens for this node")
    cost_usd: Optional[float] = Field(None, description="Estimated cost for this node in USD")
    success: bool = Field(True, description="Whether the node executed successfully")
    error_type: Optional[str] = Field(None, description="Error type if failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(0, description="Number of retries attempted")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "search_pubmed",
                "node_type": "tool",
                "start_time": "2024-01-15T10:30:10Z",
                "end_time": "2024-01-15T10:30:12Z",
                "latency_ms": 2000.0,
                "success": True,
                "retry_count": 0
            }
        }


class RAIAFunctionalSignal(BaseModel):
    """
    Represents a detected behavioral pattern or issue during execution.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: Optional[str] = Field(None, description="Node where signal was detected")
    signal_type: Literal[
        "loop_detected",
        "redundant_tool_use",
        "bad_tool_choice",
        "state_inconsistency",
        "policy_violation",
        "safety_risk",
        "suboptimal_path",
        "info_redundancy"
    ] = Field(..., description="Type of behavioral signal")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level")
    message: str = Field(..., description="Human-readable description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When signal was created")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "search_node",
                "signal_type": "redundant_tool_use",
                "severity": "medium",
                "message": "Tool 'search_pubmed' called 3 times with similar queries within 5 seconds",
                "metadata": {"tool_calls": ["call_1", "call_2", "call_3"]}
            }
        }


class RAIASemanticScore(BaseModel):
    """
    Semantic quality score for agent output or behavior.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: Optional[str] = Field(None, description="Node being evaluated")
    dimension: Literal[
        "hallucination_risk",
        "instruction_adherence",
        "business_rule_compliance",
        "answer_consistency",
        "clarity",
        "tone_appropriateness"
    ] = Field(..., description="Semantic dimension being scored")
    score: float = Field(..., description="Score value (0-1 scale)", ge=0.0, le=1.0)
    explanation: Optional[str] = Field(None, description="Explanation of the score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When score was created")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "final_answer",
                "dimension": "hallucination_risk",
                "score": 0.15,
                "explanation": "Response is well-grounded in retrieved context with minimal speculation",
                "metadata": {"evaluator": "gpt-4", "confidence": 0.89}
            }
        }
