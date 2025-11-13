"""
RAIA Explainability Models

Data models for explainability and interpretability in RAG/Agentic systems.

Unlike traditional ML (SHAP/LIME) which explains static predictions,
RAIA explains dynamic processes: retrieval, reasoning, decisions, and actions.

UNIQUE TO RAIA - No competitor offers comprehensive explainability!
"""

from datetime import datetime
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class Attribution(BaseModel):
    """
    Single attribution: Maps answer span to source document.

    Example:
        answer_span="greenhouse gas emissions"
        source_doc="doc_climate_science"
        source_span="GHG emissions from fossil fuels"
        confidence=0.95
    """
    answer_span: str = Field(..., description="Text in the generated answer")
    answer_start_idx: int = Field(..., description="Start position in answer")
    answer_end_idx: int = Field(..., description="End position in answer")

    source_doc_id: str = Field(..., description="Source document ID")
    source_span: str = Field(..., description="Original text in source document")
    source_start_idx: int = Field(..., description="Start position in source")
    source_end_idx: int = Field(..., description="End position in source")

    confidence: float = Field(..., description="Attribution confidence (0-1)", ge=0.0, le=1.0)
    similarity_score: float = Field(..., description="Semantic similarity (0-1)", ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "answer_span": "greenhouse gas emissions",
                "answer_start_idx": 45,
                "answer_end_idx": 69,
                "source_doc_id": "doc_climate_science_2023",
                "source_span": "GHG emissions from fossil fuels",
                "source_start_idx": 120,
                "source_end_idx": 151,
                "confidence": 0.95,
                "similarity_score": 0.92
            }
        }


class RAIAAttributionMap(BaseModel):
    """
    Complete attribution map for a RAG answer.

    Tracks which parts of the answer came from which source documents,
    providing transparency and enabling hallucination detection.

    Like SHAP for RAG: Shows document "importance" for each answer span.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    query: str = Field(..., description="User query")
    answer: str = Field(..., description="Generated answer")

    # Attribution mapping
    attributions: List[Attribution] = Field(
        default_factory=list,
        description="List of answer span → source document mappings"
    )

    # Confidence metrics
    overall_confidence: float = Field(
        ..., description="Overall attribution confidence (0-1)", ge=0.0, le=1.0
    )
    faithfulness_score: float = Field(
        ..., description="Answer faithfulness to sources (0-1)", ge=0.0, le=1.0
    )
    hallucination_score: float = Field(
        ..., description="Hallucination score (0=none, 1=full)", ge=0.0, le=1.0
    )

    # Context usage analysis
    total_context_tokens: int = Field(..., description="Total tokens in retrieved context")
    utilized_context_tokens: int = Field(..., description="Tokens actually used in answer")
    context_efficiency: float = Field(
        ..., description="Utilization efficiency (0-1)", ge=0.0, le=1.0
    )

    # Source diversity
    unique_sources_used: int = Field(..., description="Number of unique sources cited")
    primary_source: Optional[str] = Field(None, description="Most influential source")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When attribution was computed")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "query": "What causes climate change?",
                "answer": "Climate change is caused by greenhouse gas emissions from fossil fuels and deforestation.",
                "attributions": [
                    {
                        "answer_span": "greenhouse gas emissions",
                        "source_doc_id": "doc_climate_science",
                        "confidence": 0.95
                    }
                ],
                "overall_confidence": 0.92,
                "faithfulness_score": 0.96,
                "hallucination_score": 0.04,
                "total_context_tokens": 2500,
                "utilized_context_tokens": 1850,
                "context_efficiency": 0.74,
                "unique_sources_used": 3,
                "primary_source": "doc_climate_science"
            }
        }


class ReasoningStep(BaseModel):
    """
    Single step in a reasoning chain.

    Captures what happened, why it happened, and the outcome.
    """
    step_number: int = Field(..., description="Step sequence number")
    step_name: str = Field(..., description="Human-readable step name")
    step_type: Literal[
        "understanding",
        "retrieval",
        "synthesis",
        "generation",
        "validation",
        "decision",
        "action"
    ] = Field(..., description="Type of reasoning step")

    # What happened
    description: str = Field(..., description="What this step did")
    action_taken: Optional[str] = Field(None, description="Specific action performed")

    # Why it happened
    rationale: str = Field(..., description="Why this step was necessary")
    confidence: float = Field(..., description="Confidence in this step (0-1)", ge=0.0, le=1.0)

    # Inputs and outputs
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input data for this step")
    outputs: dict[str, Any] = Field(default_factory=dict, description="Output data from this step")

    # Timing
    start_time: datetime = Field(..., description="When step started")
    end_time: datetime = Field(..., description="When step ended")
    latency_ms: float = Field(..., description="Step duration in milliseconds")

    # Success indicator
    success: bool = Field(True, description="Did step complete successfully?")
    error_message: Optional[str] = Field(None, description="Error if step failed")

    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "step_name": "Query Understanding",
                "step_type": "understanding",
                "description": "Analyzed user query to extract intent and key concepts",
                "action_taken": "extract_intent(query)",
                "rationale": "Need to understand query intent before retrieval",
                "confidence": 0.92,
                "inputs": {"query": "What causes climate change?"},
                "outputs": {"intent": "causal_inquiry", "concepts": ["climate change", "causes"]},
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T10:00:00.050Z",
                "latency_ms": 50.0,
                "success": True
            }
        }


class RAIAReasoningTrace(BaseModel):
    """
    Complete reasoning chain for RAG/Agent execution.

    Like a detailed audit trail showing step-by-step how the system
    reasoned from query to answer.

    This is like LIME for agents: Shows local reasoning process.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    trace_type: Literal["rag_reasoning", "agent_reasoning", "hybrid"] = Field(
        ..., description="Type of reasoning trace"
    )

    # Query context
    query: str = Field(..., description="Original user query")
    final_answer: Optional[str] = Field(None, description="Final answer/output")

    # Reasoning steps
    steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="Ordered list of reasoning steps"
    )

    # Overall metrics
    total_steps: int = Field(..., description="Total number of steps")
    successful_steps: int = Field(..., description="Steps that succeeded")
    failed_steps: int = Field(0, description="Steps that failed")

    # Quality scores
    reasoning_quality_score: float = Field(
        ..., description="Overall reasoning quality (0-1)", ge=0.0, le=1.0
    )
    logical_consistency: float = Field(
        ..., description="Logical consistency score (0-1)", ge=0.0, le=1.0
    )

    # Timing
    total_latency_ms: float = Field(..., description="Total reasoning time")
    bottleneck_step: Optional[str] = Field(None, description="Slowest step name")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When trace was created")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "trace_type": "rag_reasoning",
                "query": "What causes climate change?",
                "final_answer": "Climate change is caused by greenhouse gas emissions...",
                "steps": [
                    {
                        "step_number": 1,
                        "step_name": "Query Understanding",
                        "step_type": "understanding",
                        "description": "Extracted intent and concepts",
                        "confidence": 0.92,
                        "latency_ms": 50.0
                    }
                ],
                "total_steps": 5,
                "successful_steps": 5,
                "failed_steps": 0,
                "reasoning_quality_score": 0.89,
                "logical_consistency": 0.94,
                "total_latency_ms": 1250.0,
                "bottleneck_step": "LLM Generation"
            }
        }


class AlternativeAction(BaseModel):
    """
    An alternative action that was considered but not taken.

    Helps explain "what-if" scenarios: What if the agent had chosen differently?
    """
    action_name: str = Field(..., description="Name of alternative action")
    action_description: str = Field(..., description="What this action would do")

    estimated_score: float = Field(..., description="Predicted score (0-1)", ge=0.0, le=1.0)
    estimated_latency_ms: Optional[float] = Field(None, description="Predicted latency")
    estimated_cost_usd: Optional[float] = Field(None, description="Predicted cost")

    why_not_selected: str = Field(..., description="Reason this wasn't chosen")

    pros: List[str] = Field(default_factory=list, description="Advantages of this action")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of this action")

    class Config:
        json_schema_extra = {
            "example": {
                "action_name": "web_search",
                "action_description": "Search the web for weather information",
                "estimated_score": 0.45,
                "estimated_latency_ms": 1200.0,
                "estimated_cost_usd": 0.00045,
                "why_not_selected": "get_weather_api is faster and more accurate",
                "pros": ["Finds additional context", "Broadly applicable"],
                "cons": ["Slower than API", "Less accurate", "More expensive"]
            }
        }


class RAIAAgentDecision(BaseModel):
    """
    Explains why an agent chose a specific action.

    Provides transparency into agent decision-making process.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    node_name: str = Field(..., description="Node where decision was made")
    decision_point: str = Field(..., description="What was being decided")

    # Selected action
    selected_action: str = Field(..., description="Action that was selected")
    selection_rationale: str = Field(..., description="Why this action was chosen")
    selection_confidence: float = Field(
        ..., description="Confidence in selection (0-1)", ge=0.0, le=1.0
    )

    # Context
    agent_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Agent state at decision time"
    )
    context_used: List[str] = Field(
        default_factory=list,
        description="What information was used to decide"
    )

    # Alternatives
    alternatives_considered: List[AlternativeAction] = Field(
        default_factory=list,
        description="Other actions that were considered"
    )
    num_alternatives: int = Field(0, description="Number of alternatives")

    # Outcome
    actual_outcome: Optional[str] = Field(None, description="What actually happened")
    outcome_success: Optional[bool] = Field(None, description="Was outcome successful?")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When decision was made")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "node_name": "tool_selector",
                "decision_point": "Select appropriate tool for weather query",
                "selected_action": "get_weather_api",
                "selection_rationale": "Direct weather query detected, using specialized weather API",
                "selection_confidence": 0.95,
                "agent_state": {"query": "What's the weather?", "user_location": "Paris"},
                "context_used": ["query_text", "intent_classification", "available_tools"],
                "alternatives_considered": [
                    {
                        "action_name": "web_search",
                        "estimated_score": 0.45,
                        "why_not_selected": "Less accurate and slower than API"
                    }
                ],
                "num_alternatives": 3,
                "actual_outcome": "Successfully retrieved weather data",
                "outcome_success": True
            }
        }
