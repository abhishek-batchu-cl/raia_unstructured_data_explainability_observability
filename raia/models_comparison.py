"""
RAIA Comparison & Reporting Models

Data models for comparing runs, benchmarking, and generating reports.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RunComparison(BaseModel):
    """
    Comparison between two or more runs.

    Enables A/B testing, version comparison, and performance benchmarking.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    comparison_name: str = Field(..., description="Human-readable comparison name")
    run_ids: List[str] = Field(..., description="List of run IDs being compared")

    # Aggregate metrics
    avg_quality: Dict[str, float] = Field(
        default_factory=dict,
        description="Average quality per run"
    )
    avg_latency_ms: Dict[str, float] = Field(
        default_factory=dict,
        description="Average latency per run"
    )
    avg_cost_usd: Dict[str, float] = Field(
        default_factory=dict,
        description="Average cost per run"
    )

    # Winner determination
    best_quality_run: str = Field(..., description="Run with best quality")
    best_latency_run: str = Field(..., description="Run with best latency")
    best_cost_run: str = Field(..., description="Run with best cost")
    overall_winner: str = Field(..., description="Overall best run")
    winner_rationale: str = Field(..., description="Why this run won")

    # Statistical significance
    quality_variance: float = Field(..., description="Quality variance across runs")
    latency_variance: float = Field(..., description="Latency variance across runs")
    cost_variance: float = Field(..., description="Cost variance across runs")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When comparison was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "comparison_name": "GPT-4 vs GPT-3.5 comparison",
                "run_ids": ["run_gpt4_001", "run_gpt35_001"],
                "avg_quality": {"run_gpt4_001": 0.94, "run_gpt35_001": 0.86},
                "avg_latency_ms": {"run_gpt4_001": 2200.0, "run_gpt35_001": 1100.0},
                "avg_cost_usd": {"run_gpt4_001": 0.015, "run_gpt35_001": 0.002},
                "best_quality_run": "run_gpt4_001",
                "best_latency_run": "run_gpt35_001",
                "best_cost_run": "run_gpt35_001",
                "overall_winner": "run_gpt4_001",
                "winner_rationale": "Higher quality justifies cost increase for this use case",
                "quality_variance": 0.008,
                "latency_variance": 550.0,
                "cost_variance": 0.0065
            }
        }


class EvaluationReport(BaseModel):
    """
    Comprehensive evaluation report for a run or set of runs.

    Aggregates all metrics, explainability, and what-if analysis into a
    single comprehensive report.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    report_name: str = Field(..., description="Report title")
    run_ids: List[str] = Field(..., description="Runs included in report")

    # Summary metrics
    total_queries: int = Field(..., description="Total queries evaluated")
    avg_quality: float = Field(..., description="Average quality score", ge=0.0, le=1.0)
    avg_latency_ms: float = Field(..., description="Average latency")
    avg_cost_usd: float = Field(..., description="Average cost per query")

    # Quality breakdown
    quality_excellent: int = Field(0, description="Queries with quality >= 0.9")
    quality_good: int = Field(0, description="Queries with quality >= 0.7")
    quality_poor: int = Field(0, description="Queries with quality < 0.7")

    # Explainability summary
    avg_faithfulness: Optional[float] = Field(None, description="Average faithfulness score")
    avg_hallucination: Optional[float] = Field(None, description="Average hallucination score")

    # What-if insights
    optimization_opportunities: int = Field(0, description="Number of optimization opportunities found")
    potential_annual_savings_usd: Optional[float] = Field(None, description="Potential annual savings")

    # Key insights
    strengths: List[str] = Field(default_factory=list, description="System strengths")
    weaknesses: List[str] = Field(default_factory=list, description="System weaknesses")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When report was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "report_name": "Q4 2024 RAG System Evaluation",
                "run_ids": ["run_001", "run_002", "run_003"],
                "total_queries": 1500,
                "avg_quality": 0.89,
                "avg_latency_ms": 1350.0,
                "avg_cost_usd": 0.0032,
                "quality_excellent": 750,
                "quality_good": 600,
                "quality_poor": 150,
                "avg_faithfulness": 0.96,
                "avg_hallucination": 0.04,
                "optimization_opportunities": 3,
                "potential_annual_savings_usd": 125000.0,
                "strengths": [
                    "High faithfulness (96%)",
                    "Low hallucination rate (4%)",
                    "Consistent quality across runs"
                ],
                "weaknesses": [
                    "High latency for complex queries",
                    "Cost inefficiency in retrieval",
                    "10% of queries have poor quality"
                ],
                "recommendations": [
                    "Implement query result caching",
                    "Optimize retrieval strategy",
                    "Add query complexity routing"
                ]
            }
        }


class BatchEvaluationResult(BaseModel):
    """
    Results from evaluating multiple queries in batch.

    Enables efficient evaluation of test sets and benchmarks.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    batch_name: str = Field(..., description="Batch evaluation name")
    run_id: str = Field(..., description="Associated run ID")

    # Batch details
    total_queries: int = Field(..., description="Total queries in batch")
    successful_queries: int = Field(..., description="Successfully evaluated queries")
    failed_queries: int = Field(0, description="Failed queries")

    # Aggregate metrics
    avg_quality: float = Field(..., description="Average quality", ge=0.0, le=1.0)
    min_quality: float = Field(..., description="Minimum quality", ge=0.0, le=1.0)
    max_quality: float = Field(..., description="Maximum quality", ge=0.0, le=1.0)
    std_quality: float = Field(..., description="Quality standard deviation")

    avg_latency_ms: float = Field(..., description="Average latency")
    min_latency_ms: float = Field(..., description="Minimum latency")
    max_latency_ms: float = Field(..., description="Maximum latency")

    total_cost_usd: float = Field(..., description="Total cost for batch")
    avg_cost_usd: float = Field(..., description="Average cost per query")

    # Timing
    batch_start_time: datetime = Field(..., description="When batch started")
    batch_end_time: datetime = Field(..., description="When batch ended")
    total_duration_ms: float = Field(..., description="Total batch duration")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="When result was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_name": "Benchmark Test Set v2.1",
                "run_id": "batch_run_001",
                "total_queries": 100,
                "successful_queries": 98,
                "failed_queries": 2,
                "avg_quality": 0.87,
                "min_quality": 0.52,
                "max_quality": 0.98,
                "std_quality": 0.12,
                "avg_latency_ms": 1450.0,
                "min_latency_ms": 850.0,
                "max_latency_ms": 3200.0,
                "total_cost_usd": 0.42,
                "avg_cost_usd": 0.0042,
                "batch_start_time": "2024-01-15T10:00:00Z",
                "batch_end_time": "2024-01-15T10:02:30Z",
                "total_duration_ms": 150000.0
            }
        }
