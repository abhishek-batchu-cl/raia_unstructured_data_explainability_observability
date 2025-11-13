"""
RAIA What-If Analysis Models

Data models for counterfactual analysis and optimization in RAG/Agentic systems.

UNIQUE TO RAIA - No competitor offers comprehensive what-if analysis!
Enables proactive optimization and risk assessment.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class RAIACounterfactualScenario(BaseModel):
    """
    What-if scenario: "What would happen if we changed X?"

    Enables exploration of alternative configurations and their impact
    on quality, latency, cost, and other metrics.

    Example scenarios:
    - What if we retrieved 10 docs instead of 5?
    - What if we used a smaller LLM?
    - What if embeddings drifted by 0.05 KL divergence?
    - What if we disabled reranking?
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID for comparison")
    scenario_name: str = Field(..., description="Human-readable scenario name")

    scenario_type: Literal[
        "retrieval",           # Different retrieval strategy
        "context",             # Different context size/strategy
        "tool_selection",      # Different tool choice
        "agent_path",          # Different graph path
        "parameter",           # Different hyperparameters
        "drift_simulation",    # Simulated embedding drift
        "cost_optimization",   # Cost reduction strategies
        "quality_optimization" # Quality improvement strategies
    ] = Field(..., description="Type of what-if scenario")

    # Original configuration
    original_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original configuration parameters"
    )

    # Alternative configuration
    alternative_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Alternative configuration to test"
    )

    # Original metrics
    original_quality: float = Field(..., description="Original quality score (0-1)", ge=0.0, le=1.0)
    original_latency_ms: float = Field(..., description="Original latency (ms)")
    original_cost_usd: float = Field(..., description="Original cost (USD)")
    original_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional original metrics")

    # Alternative metrics (simulated or actual)
    alternative_quality: float = Field(..., description="Alternative quality score (0-1)", ge=0.0, le=1.0)
    alternative_latency_ms: float = Field(..., description="Alternative latency (ms)")
    alternative_cost_usd: float = Field(..., description="Alternative cost (USD)")
    alternative_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional alternative metrics")

    # Impact analysis
    quality_delta: float = Field(..., description="Quality change (positive = improvement)")
    quality_delta_pct: float = Field(..., description="Quality change percentage")
    latency_delta_ms: float = Field(..., description="Latency change (negative = faster)")
    latency_delta_pct: float = Field(..., description="Latency change percentage")
    cost_delta_usd: float = Field(..., description="Cost change (negative = cheaper)")
    cost_delta_pct: float = Field(..., description="Cost change percentage")

    # Recommendation
    is_improvement: bool = Field(..., description="Is alternative better overall?")
    recommendation: Literal["adopt", "reject", "test_further", "conditional"] = Field(
        ..., description="What action to take"
    )
    recommendation_rationale: str = Field(..., description="Why this recommendation?")
    confidence: float = Field(..., description="Confidence in recommendation (0-1)", ge=0.0, le=1.0)

    # Trade-offs
    pros: List[str] = Field(default_factory=list, description="Advantages of alternative")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of alternative")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When scenario was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "scenario_name": "Increase retrieval from 5 to 10 documents",
                "scenario_type": "retrieval",
                "original_config": {"num_docs": 5, "rerank": True},
                "alternative_config": {"num_docs": 10, "rerank": True},
                "original_quality": 0.89,
                "original_latency_ms": 1200.0,
                "original_cost_usd": 0.0018,
                "alternative_quality": 0.91,
                "alternative_latency_ms": 2100.0,
                "alternative_cost_usd": 0.0034,
                "quality_delta": 0.02,
                "quality_delta_pct": 2.25,
                "latency_delta_ms": 900.0,
                "latency_delta_pct": 75.0,
                "cost_delta_usd": 0.0016,
                "cost_delta_pct": 88.89,
                "is_improvement": False,
                "recommendation": "reject",
                "recommendation_rationale": "Quality gain (+2%) doesn't justify latency increase (+75%) and cost increase (+89%)",
                "confidence": 0.92,
                "pros": ["Slightly better quality", "More context"],
                "cons": ["Much slower", "Much more expensive", "Diminishing returns"]
            }
        }


class ParameterSensitivity(BaseModel):
    """
    Sensitivity of a single parameter.

    Shows how much output changes when parameter changes.
    """
    parameter_name: str = Field(..., description="Name of parameter")
    parameter_type: str = Field(..., description="Type of parameter (int, float, str, etc.)")

    # Value range tested
    min_value: Any = Field(..., description="Minimum value tested")
    max_value: Any = Field(..., description="Maximum value tested")
    num_samples: int = Field(..., description="Number of values tested")

    # Sensitivity metrics
    quality_sensitivity: float = Field(
        ..., description="Quality sensitivity (0-1, higher = more sensitive)", ge=0.0, le=1.0
    )
    latency_sensitivity: float = Field(
        ..., description="Latency sensitivity (0-1)", ge=0.0, le=1.0
    )
    cost_sensitivity: float = Field(
        ..., description="Cost sensitivity (0-1)", ge=0.0, le=1.0
    )

    # Optimal value
    optimal_value: Any = Field(..., description="Optimal parameter value")
    optimal_rationale: str = Field(..., description="Why this value is optimal")

    # Impact assessment
    impact_level: Literal["critical", "high", "medium", "low", "negligible"] = Field(
        ..., description="Overall impact level"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "parameter_name": "num_retrieved_docs",
                "parameter_type": "int",
                "min_value": 1,
                "max_value": 20,
                "num_samples": 10,
                "quality_sensitivity": 0.72,
                "latency_sensitivity": 0.45,
                "cost_sensitivity": 0.38,
                "optimal_value": 5,
                "optimal_rationale": "Best quality/cost/latency trade-off",
                "impact_level": "high"
            }
        }


class RAIASensitivityAnalysis(BaseModel):
    """
    Sensitivity analysis: How do parameters affect outcomes?

    Tests multiple parameter values to find optimal configuration.
    Identifies which parameters have the most impact.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    analysis_name: str = Field(..., description="Human-readable analysis name")

    # Parameters analyzed
    parameters: List[ParameterSensitivity] = Field(
        default_factory=list,
        description="List of parameter sensitivities"
    )

    # Overall insights
    most_sensitive_param: str = Field(..., description="Parameter with highest sensitivity")
    least_sensitive_param: str = Field(..., description="Parameter with lowest sensitivity")

    # Optimal configuration
    optimal_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Recommended optimal configuration"
    )
    expected_improvement: float = Field(
        ..., description="Expected improvement vs baseline (0-1)", ge=0.0, le=1.0
    )

    # Analysis metadata
    num_simulations: int = Field(..., description="Total simulations run")
    analysis_duration_ms: float = Field(..., description="Time taken for analysis")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "analysis_name": "RAG Pipeline Parameter Sensitivity",
                "parameters": [
                    {
                        "parameter_name": "num_retrieved_docs",
                        "quality_sensitivity": 0.72,
                        "optimal_value": 5
                    }
                ],
                "most_sensitive_param": "num_retrieved_docs",
                "least_sensitive_param": "temperature",
                "optimal_config": {"num_retrieved_docs": 5, "temperature": 0.2},
                "expected_improvement": 0.15,
                "num_simulations": 100,
                "analysis_duration_ms": 45000.0
            }
        }


class RAIAOptimizationRecommendation(BaseModel):
    """
    Optimization recommendation: Actionable suggestions to improve system.

    Based on what-if analysis and sensitivity analysis, provides concrete
    recommendations for improving quality, reducing latency, or cutting costs.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    run_id: str = Field(..., description="Parent run ID")
    recommendation_name: str = Field(..., description="Short recommendation title")

    optimization_goal: Literal[
        "quality",              # Improve quality
        "latency",              # Reduce latency
        "cost",                 # Reduce cost
        "balanced",             # Balance all three
        "quality_cost",         # Quality + cost
        "quality_latency",      # Quality + latency
        "cost_latency"          # Cost + latency
    ] = Field(..., description="Primary optimization goal")

    # Current state
    current_quality: float = Field(..., description="Current quality (0-1)", ge=0.0, le=1.0)
    current_latency_ms: float = Field(..., description="Current latency (ms)")
    current_cost_usd: float = Field(..., description="Current cost (USD)")

    # Recommended changes
    recommended_changes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Specific changes to make"
    )

    # Expected outcomes
    expected_quality: float = Field(..., description="Expected quality after changes (0-1)", ge=0.0, le=1.0)
    expected_latency_ms: float = Field(..., description="Expected latency after changes (ms)")
    expected_cost_usd: float = Field(..., description="Expected cost after changes (USD)")

    # Impact summary
    quality_improvement_pct: float = Field(..., description="Quality improvement %")
    latency_improvement_pct: float = Field(..., description="Latency improvement % (negative = slower)")
    cost_savings_pct: float = Field(..., description="Cost savings % (negative = more expensive)")

    # Implementation
    implementation_difficulty: Literal["easy", "medium", "hard", "very_hard"] = Field(
        ..., description="How hard to implement"
    )
    implementation_steps: List[str] = Field(
        default_factory=list,
        description="Step-by-step implementation guide"
    )
    estimated_implementation_time: str = Field(..., description="Estimated time to implement")

    # Risk assessment
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Risk level of this change"
    )
    risks: List[str] = Field(default_factory=list, description="Potential risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="How to mitigate risks")

    # Priority
    priority: Literal["critical", "high", "medium", "low"] = Field(
        ..., description="Implementation priority"
    )
    priority_rationale: str = Field(..., description="Why this priority?")

    # ROI estimation
    estimated_annual_savings_usd: Optional[float] = Field(None, description="Annual cost savings")
    estimated_roi_pct: Optional[float] = Field(None, description="Return on investment %")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When recommendation was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "run_abc123",
                "recommendation_name": "Implement query result caching",
                "optimization_goal": "cost_latency",
                "current_quality": 0.89,
                "current_latency_ms": 1200.0,
                "current_cost_usd": 0.0018,
                "recommended_changes": {
                    "add_redis_cache": True,
                    "cache_ttl_hours": 24,
                    "cache_hit_rate_target": 0.30
                },
                "expected_quality": 0.89,
                "expected_latency_ms": 850.0,
                "expected_cost_usd": 0.0013,
                "quality_improvement_pct": 0.0,
                "latency_improvement_pct": -29.2,
                "cost_savings_pct": -27.8,
                "implementation_difficulty": "medium",
                "implementation_steps": [
                    "Set up Redis instance",
                    "Implement cache key generation",
                    "Add cache lookup logic",
                    "Monitor cache hit rate"
                ],
                "estimated_implementation_time": "2-3 days",
                "risk_level": "low",
                "risks": ["Stale data if TTL too long", "Cache misses on first query"],
                "mitigation_strategies": ["Use reasonable TTL", "Implement cache warming"],
                "priority": "high",
                "priority_rationale": "High impact, low risk, moderate effort",
                "estimated_annual_savings_usd": 12500.0,
                "estimated_roi_pct": 450.0
            }
        }
