"""
RAIA Inspectors - SQLite Storage Implementation

SQLite-based storage backend for inspector metrics.
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from raia.storage.base import BaseRAIAStorage
from raia.models import (
    RAIAAgentRun,
    RAIANodeMetrics,
    RAIAFunctionalSignal,
    RAIASemanticScore,
    # RAG Evaluation Models
    RAIARetrievalMetrics,
    RAIAAnswerQualityMetrics,
    RAIAEmbeddingDriftMetrics,
    RAIAVectorIndexHealth,
    RAIAPipelineMetrics,
)
from raia.models_explainability import (
    RAIAAttributionMap,
    RAIAReasoningTrace,
    RAIAAgentDecision,
)
from raia.models_whatif import (
    RAIACounterfactualScenario,
    ParameterSensitivity,
    RAIASensitivityAnalysis,
    RAIAOptimizationRecommendation,
)


logger = logging.getLogger(__name__)


class SQLiteRAIAStorage(BaseRAIAStorage):
    """
    SQLite-based storage implementation for RAIA inspectors.

    Provides persistent storage with automatic schema creation and management.
    """

    def __init__(self, db_path: str = "raia_inspectors.db"):
        """
        Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._create_tables()
        logger.info(f"Initialized SQLite storage at {db_path}")

    def _ensure_db_exists(self) -> None:
        """Ensure database file and parent directories exist."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create raia_runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_runs (
                    run_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    agent_name TEXT,
                    graph_name TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    total_latency_ms REAL,
                    total_tokens_prompt INTEGER,
                    total_tokens_completion INTEGER,
                    total_cost_usd REAL,
                    task_completed BOOLEAN,
                    task_completion_rate REAL,
                    goal_achieved BOOLEAN,
                    goal_achievement_score REAL,
                    success_criteria TEXT,
                    criteria_met TEXT,
                    time_to_first_token_ms REAL,
                    tokens_per_second REAL,
                    streaming_enabled BOOLEAN,
                    error_count INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    recovery_successful BOOLEAN,
                    fallback_used BOOLEAN,
                    metadata TEXT
                )
            """)

            # Add new columns to existing tables (for backward compatibility)
            self._add_missing_columns(cursor)

            # Create raia_node_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_node_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    node_name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    tokens_prompt INTEGER,
                    tokens_completion INTEGER,
                    cost_usd REAL,
                    success BOOLEAN NOT NULL,
                    error_type TEXT,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_functional_signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_functional_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    node_name TEXT,
                    signal_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_semantic_scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_semantic_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    node_name TEXT,
                    dimension TEXT NOT NULL,
                    score REAL NOT NULL,
                    explanation TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # =================================================================
            # RAG EVALUATION TABLES
            # =================================================================

            # Create raia_retrieval_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_retrieval_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    retrieved_count INTEGER NOT NULL,
                    precision_at_k REAL,
                    recall_at_k REAL,
                    mrr REAL,
                    ndcg REAL,
                    retrieval_latency_ms REAL NOT NULL,
                    rerank_latency_ms REAL,
                    total_latency_ms REAL NOT NULL,
                    context_relevance_score REAL,
                    context_diversity REAL,
                    context_coverage REAL,
                    retrieved_doc_ids TEXT,
                    relevance_scores TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_answer_quality_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_answer_quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    answer_faithfulness REAL,
                    hallucination_score REAL,
                    citation_accuracy REAL,
                    answer_relevance REAL,
                    answer_completeness REAL,
                    answer_conciseness REAL,
                    context_utilization REAL,
                    context_recall REAL,
                    self_contradiction BOOLEAN,
                    context_contradiction BOOLEAN,
                    generation_latency_ms REAL,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_embedding_drift_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_embedding_drift_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    index_name TEXT NOT NULL,
                    kl_divergence REAL,
                    js_divergence REAL,
                    wasserstein_distance REAL,
                    avg_similarity_to_baseline REAL,
                    similarity_distribution_shift REAL,
                    drift_detected BOOLEAN NOT NULL,
                    drift_severity TEXT NOT NULL,
                    drift_threshold REAL,
                    baseline_period_start TEXT,
                    baseline_period_end TEXT,
                    current_period_start TEXT,
                    current_period_end TEXT,
                    samples_analyzed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Create raia_vector_index_health table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_vector_index_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    index_name TEXT NOT NULL,
                    total_documents INTEGER NOT NULL,
                    total_embeddings INTEGER NOT NULL,
                    index_size_mb REAL,
                    avg_query_latency_ms REAL NOT NULL,
                    p50_latency_ms REAL,
                    p95_latency_ms REAL,
                    p99_latency_ms REAL,
                    avg_recall_at_10 REAL,
                    recall_degradation_pct REAL,
                    last_updated TEXT NOT NULL,
                    staleness_hours REAL NOT NULL,
                    pending_updates INTEGER NOT NULL,
                    memory_usage_mb REAL,
                    cpu_usage_pct REAL,
                    disk_usage_mb REAL,
                    health_status TEXT NOT NULL,
                    health_issues TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # Create raia_pipeline_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_pipeline_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    pipeline_name TEXT NOT NULL,
                    query_preprocessing_ms REAL NOT NULL,
                    embedding_generation_ms REAL NOT NULL,
                    vector_search_ms REAL NOT NULL,
                    reranking_ms REAL,
                    llm_generation_ms REAL NOT NULL,
                    postprocessing_ms REAL NOT NULL,
                    total_pipeline_ms REAL NOT NULL,
                    stages_completed INTEGER NOT NULL,
                    stages_failed INTEGER NOT NULL,
                    failed_stage TEXT,
                    embedding_tokens INTEGER NOT NULL,
                    llm_prompt_tokens INTEGER NOT NULL,
                    llm_completion_tokens INTEGER NOT NULL,
                    embedding_cost_usd REAL NOT NULL,
                    llm_cost_usd REAL NOT NULL,
                    total_cost_usd REAL NOT NULL,
                    pipeline_success BOOLEAN NOT NULL,
                    quality_score REAL,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # =================================================================
            # EXPLAINABILITY TABLES
            # =================================================================

            # Create raia_attribution_maps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_attribution_maps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    attributions TEXT NOT NULL,
                    overall_confidence REAL NOT NULL,
                    faithfulness_score REAL NOT NULL,
                    hallucination_score REAL NOT NULL,
                    total_context_tokens INTEGER NOT NULL,
                    utilized_context_tokens INTEGER NOT NULL,
                    context_efficiency REAL NOT NULL,
                    unique_sources_used INTEGER NOT NULL,
                    primary_source TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_reasoning_traces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_reasoning_traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    trace_type TEXT NOT NULL,
                    query TEXT NOT NULL,
                    final_answer TEXT,
                    steps TEXT NOT NULL,
                    total_steps INTEGER NOT NULL,
                    successful_steps INTEGER NOT NULL,
                    failed_steps INTEGER NOT NULL,
                    reasoning_quality_score REAL NOT NULL,
                    logical_consistency REAL NOT NULL,
                    total_latency_ms REAL NOT NULL,
                    bottleneck_step TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_agent_decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_agent_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    node_name TEXT NOT NULL,
                    decision_point TEXT NOT NULL,
                    selected_action TEXT NOT NULL,
                    selection_rationale TEXT NOT NULL,
                    selection_confidence REAL NOT NULL,
                    agent_state TEXT,
                    context_used TEXT,
                    alternatives_considered TEXT,
                    num_alternatives INTEGER NOT NULL,
                    actual_outcome TEXT,
                    outcome_success BOOLEAN,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_counterfactual_scenarios table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_counterfactual_scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    scenario_name TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    original_config TEXT NOT NULL,
                    alternative_config TEXT NOT NULL,
                    original_quality REAL NOT NULL,
                    original_latency_ms REAL NOT NULL,
                    original_cost_usd REAL NOT NULL,
                    original_metadata TEXT,
                    alternative_quality REAL NOT NULL,
                    alternative_latency_ms REAL NOT NULL,
                    alternative_cost_usd REAL NOT NULL,
                    alternative_metadata TEXT,
                    quality_delta REAL NOT NULL,
                    quality_delta_pct REAL NOT NULL,
                    latency_delta_ms REAL NOT NULL,
                    latency_delta_pct REAL NOT NULL,
                    cost_delta_usd REAL NOT NULL,
                    cost_delta_pct REAL NOT NULL,
                    is_improvement BOOLEAN NOT NULL,
                    recommendation TEXT NOT NULL,
                    recommendation_rationale TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    pros TEXT,
                    cons TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_sensitivity_analyses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_sensitivity_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    analysis_name TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    most_sensitive_param TEXT NOT NULL,
                    least_sensitive_param TEXT NOT NULL,
                    optimal_config TEXT NOT NULL,
                    expected_improvement REAL NOT NULL,
                    num_simulations INTEGER NOT NULL,
                    analysis_duration_ms REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create raia_optimization_recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raia_optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    recommendation_name TEXT NOT NULL,
                    optimization_goal TEXT NOT NULL,
                    current_quality REAL NOT NULL,
                    current_latency_ms REAL NOT NULL,
                    current_cost_usd REAL NOT NULL,
                    recommended_changes TEXT NOT NULL,
                    expected_quality REAL NOT NULL,
                    expected_latency_ms REAL NOT NULL,
                    expected_cost_usd REAL NOT NULL,
                    quality_improvement_pct REAL NOT NULL,
                    latency_improvement_pct REAL NOT NULL,
                    cost_savings_pct REAL NOT NULL,
                    implementation_difficulty TEXT NOT NULL,
                    implementation_steps TEXT NOT NULL,
                    estimated_implementation_time TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    risks TEXT NOT NULL,
                    mitigation_strategies TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    priority_rationale TEXT NOT NULL,
                    estimated_annual_savings_usd REAL,
                    estimated_roi_pct REAL,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES raia_runs(run_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_metrics_run_id ON raia_node_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_run_id ON raia_functional_signals(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_run_id ON raia_semantic_scores(run_id)")

            # Create indexes for RAG tables
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_retrieval_metrics_run_id ON raia_retrieval_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_retrieval_metrics_created_at ON raia_retrieval_metrics(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answer_quality_run_id ON raia_answer_quality_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answer_quality_created_at ON raia_answer_quality_metrics(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_drift_metrics_index ON raia_embedding_drift_metrics(index_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_drift_metrics_created_at ON raia_embedding_drift_metrics(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_index_health_name ON raia_vector_index_health(index_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_index_health_created_at ON raia_vector_index_health(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pipeline_metrics_run_id ON raia_pipeline_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pipeline_metrics_created_at ON raia_pipeline_metrics(created_at)")

            # Create indexes for Explainability tables
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attribution_maps_run_id ON raia_attribution_maps(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attribution_maps_created_at ON raia_attribution_maps(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reasoning_traces_run_id ON raia_reasoning_traces(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reasoning_traces_created_at ON raia_reasoning_traces(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_decisions_run_id ON raia_agent_decisions(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_decisions_created_at ON raia_agent_decisions(created_at)")

            # Create indexes for What-If Analysis tables
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_counterfactual_scenarios_run_id ON raia_counterfactual_scenarios(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_counterfactual_scenarios_created_at ON raia_counterfactual_scenarios(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_counterfactual_scenarios_type ON raia_counterfactual_scenarios(scenario_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensitivity_analyses_run_id ON raia_sensitivity_analyses(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensitivity_analyses_created_at ON raia_sensitivity_analyses(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_run_id ON raia_optimization_recommendations(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_created_at ON raia_optimization_recommendations(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_optimization_recommendations_priority ON raia_optimization_recommendations(priority)")

            conn.commit()

    def _add_missing_columns(self, cursor: sqlite3.Cursor) -> None:
        """Add new columns to existing tables for backward compatibility."""
        # Get existing columns
        cursor.execute("PRAGMA table_info(raia_runs)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # Add new columns if they don't exist
        new_columns = {
            "task_completed": "BOOLEAN",
            "task_completion_rate": "REAL",
            "goal_achieved": "BOOLEAN",
            "goal_achievement_score": "REAL",
            "success_criteria": "TEXT",
            "criteria_met": "TEXT",
            "time_to_first_token_ms": "REAL",
            "tokens_per_second": "REAL",
            "streaming_enabled": "BOOLEAN",
            "error_count": "INTEGER DEFAULT 0",
            "retry_count": "INTEGER DEFAULT 0",
            "recovery_successful": "BOOLEAN",
            "fallback_used": "BOOLEAN"
        }

        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE raia_runs ADD COLUMN {column_name} {column_type}")
                    logger.info(f"Added column {column_name} to raia_runs table")
                except sqlite3.OperationalError as e:
                    logger.warning(f"Could not add column {column_name}: {e}")

    def save_run(self, run: RAIAAgentRun) -> None:
        """Save a new agent run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_runs (
                    run_id, session_id, agent_name, graph_name, start_time, end_time,
                    status, total_latency_ms, total_tokens_prompt, total_tokens_completion,
                    total_cost_usd, task_completed, task_completion_rate, goal_achieved,
                    goal_achievement_score, success_criteria, criteria_met,
                    time_to_first_token_ms, tokens_per_second, streaming_enabled,
                    error_count, retry_count, recovery_successful, fallback_used, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.run_id,
                run.session_id,
                run.agent_name,
                run.graph_name,
                run.start_time.isoformat(),
                run.end_time.isoformat() if run.end_time else None,
                run.status,
                run.total_latency_ms,
                run.total_tokens_prompt,
                run.total_tokens_completion,
                run.total_cost_usd,
                run.task_completed,
                run.task_completion_rate,
                run.goal_achieved,
                run.goal_achievement_score,
                json.dumps(run.success_criteria) if run.success_criteria else None,
                json.dumps(run.criteria_met) if run.criteria_met else None,
                run.time_to_first_token_ms,
                run.tokens_per_second,
                run.streaming_enabled,
                run.error_count,
                run.retry_count,
                run.recovery_successful,
                run.fallback_used,
                json.dumps(run.metadata) if run.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved run {run.run_id}")

    def update_run(self, run: RAIAAgentRun) -> None:
        """Update an existing agent run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE raia_runs SET
                    session_id = ?,
                    agent_name = ?,
                    graph_name = ?,
                    start_time = ?,
                    end_time = ?,
                    status = ?,
                    total_latency_ms = ?,
                    total_tokens_prompt = ?,
                    total_tokens_completion = ?,
                    total_cost_usd = ?,
                    task_completed = ?,
                    task_completion_rate = ?,
                    goal_achieved = ?,
                    goal_achievement_score = ?,
                    success_criteria = ?,
                    criteria_met = ?,
                    time_to_first_token_ms = ?,
                    tokens_per_second = ?,
                    streaming_enabled = ?,
                    error_count = ?,
                    retry_count = ?,
                    recovery_successful = ?,
                    fallback_used = ?,
                    metadata = ?
                WHERE run_id = ?
            """, (
                run.session_id,
                run.agent_name,
                run.graph_name,
                run.start_time.isoformat(),
                run.end_time.isoformat() if run.end_time else None,
                run.status,
                run.total_latency_ms,
                run.total_tokens_prompt,
                run.total_tokens_completion,
                run.total_cost_usd,
                run.task_completed,
                run.task_completion_rate,
                run.goal_achieved,
                run.goal_achievement_score,
                json.dumps(run.success_criteria) if run.success_criteria else None,
                json.dumps(run.criteria_met) if run.criteria_met else None,
                run.time_to_first_token_ms,
                run.tokens_per_second,
                run.streaming_enabled,
                run.error_count,
                run.retry_count,
                run.recovery_successful,
                run.fallback_used,
                json.dumps(run.metadata) if run.metadata else None,
                run.run_id
            ))
            conn.commit()
            logger.debug(f"Updated run {run.run_id}")

    def save_node_metrics(self, metrics: RAIANodeMetrics) -> None:
        """Save node metrics for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_node_metrics (
                    run_id, node_name, node_type, start_time, end_time, latency_ms,
                    tokens_prompt, tokens_completion, cost_usd, success, error_type,
                    error_message, retry_count, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.run_id,
                metrics.node_name,
                metrics.node_type,
                metrics.start_time.isoformat(),
                metrics.end_time.isoformat(),
                metrics.latency_ms,
                metrics.tokens_prompt,
                metrics.tokens_completion,
                metrics.cost_usd,
                metrics.success,
                metrics.error_type,
                metrics.error_message,
                metrics.retry_count,
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved node metrics for {metrics.node_name} in run {metrics.run_id}")

    def save_functional_signal(self, signal: RAIAFunctionalSignal) -> None:
        """Save a functional signal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_functional_signals (
                    run_id, node_name, signal_type, severity, message, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal.run_id,
                signal.node_name,
                signal.signal_type,
                signal.severity,
                signal.message,
                signal.created_at.isoformat(),
                json.dumps(signal.metadata) if signal.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved signal {signal.signal_type} for run {signal.run_id}")

    def save_semantic_score(self, score: RAIASemanticScore) -> None:
        """Save a semantic quality score."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_semantic_scores (
                    run_id, node_name, dimension, score, explanation, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                score.run_id,
                score.node_name,
                score.dimension,
                score.score,
                score.explanation,
                score.created_at.isoformat(),
                json.dumps(score.metadata) if score.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved semantic score {score.dimension} for run {score.run_id}")

    def get_run(self, run_id: str) -> Optional[RAIAAgentRun]:
        """Retrieve a run by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return RAIAAgentRun(
                run_id=row["run_id"],
                session_id=row["session_id"],
                agent_name=row["agent_name"],
                graph_name=row["graph_name"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                status=row["status"],
                total_latency_ms=row["total_latency_ms"],
                total_tokens_prompt=row["total_tokens_prompt"],
                total_tokens_completion=row["total_tokens_completion"],
                total_cost_usd=row["total_cost_usd"],
                task_completed=bool(row["task_completed"]) if row["task_completed"] is not None else None,
                task_completion_rate=row["task_completion_rate"],
                goal_achieved=bool(row["goal_achieved"]) if row["goal_achieved"] is not None else None,
                goal_achievement_score=row["goal_achievement_score"],
                success_criteria=json.loads(row["success_criteria"]) if row["success_criteria"] else None,
                criteria_met=json.loads(row["criteria_met"]) if row["criteria_met"] else None,
                time_to_first_token_ms=row["time_to_first_token_ms"],
                tokens_per_second=row["tokens_per_second"],
                streaming_enabled=bool(row["streaming_enabled"]) if row["streaming_enabled"] is not None else None,
                error_count=row["error_count"] if row["error_count"] is not None else 0,
                retry_count=row["retry_count"] if row["retry_count"] is not None else 0,
                recovery_successful=bool(row["recovery_successful"]) if row["recovery_successful"] is not None else None,
                fallback_used=bool(row["fallback_used"]) if row["fallback_used"] is not None else None,
                metadata=json.loads(row["metadata"]) if row["metadata"] else None
            )

    def get_node_metrics_for_run(self, run_id: str) -> list[RAIANodeMetrics]:
        """Retrieve all node metrics for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_node_metrics WHERE run_id = ? ORDER BY start_time", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIANodeMetrics(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_name=row["node_name"],
                    node_type=row["node_type"],
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]),
                    latency_ms=row["latency_ms"],
                    tokens_prompt=row["tokens_prompt"],
                    tokens_completion=row["tokens_completion"],
                    cost_usd=row["cost_usd"],
                    success=bool(row["success"]),
                    error_type=row["error_type"],
                    error_message=row["error_message"],
                    retry_count=row["retry_count"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_signals_for_run(self, run_id: str) -> list[RAIAFunctionalSignal]:
        """Retrieve all functional signals for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_functional_signals WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAFunctionalSignal(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_name=row["node_name"],
                    signal_type=row["signal_type"],
                    severity=row["severity"],
                    message=row["message"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_semantic_scores_for_run(self, run_id: str) -> list[RAIASemanticScore]:
        """Retrieve all semantic scores for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_semantic_scores WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIASemanticScore(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_name=row["node_name"],
                    dimension=row["dimension"],
                    score=row["score"],
                    explanation=row["explanation"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    # =================================================================
    # RAG EVALUATION METHODS
    # =================================================================

    def save_retrieval_metrics(self, metrics: RAIARetrievalMetrics) -> None:
        """Save retrieval metrics for a RAG run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_retrieval_metrics (
                    run_id, query, retrieved_count, precision_at_k, recall_at_k, mrr, ndcg,
                    retrieval_latency_ms, rerank_latency_ms, total_latency_ms,
                    context_relevance_score, context_diversity, context_coverage,
                    retrieved_doc_ids, relevance_scores, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.run_id,
                metrics.query,
                metrics.retrieved_count,
                metrics.precision_at_k,
                metrics.recall_at_k,
                metrics.mrr,
                metrics.ndcg,
                metrics.retrieval_latency_ms,
                metrics.rerank_latency_ms,
                metrics.total_latency_ms,
                metrics.context_relevance_score,
                metrics.context_diversity,
                metrics.context_coverage,
                json.dumps(metrics.retrieved_doc_ids) if metrics.retrieved_doc_ids else None,
                json.dumps(metrics.relevance_scores) if metrics.relevance_scores else None,
                metrics.created_at.isoformat(),
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved retrieval metrics for run {metrics.run_id}")

    def save_answer_quality_metrics(self, metrics: RAIAAnswerQualityMetrics) -> None:
        """Save answer quality metrics for a RAG run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_answer_quality_metrics (
                    run_id, query, answer, answer_faithfulness, hallucination_score,
                    citation_accuracy, answer_relevance, answer_completeness, answer_conciseness,
                    context_utilization, context_recall, self_contradiction, context_contradiction,
                    generation_latency_ms, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.run_id,
                metrics.query,
                metrics.answer,
                metrics.answer_faithfulness,
                metrics.hallucination_score,
                metrics.citation_accuracy,
                metrics.answer_relevance,
                metrics.answer_completeness,
                metrics.answer_conciseness,
                metrics.context_utilization,
                metrics.context_recall,
                metrics.self_contradiction,
                metrics.context_contradiction,
                metrics.generation_latency_ms,
                metrics.created_at.isoformat(),
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved answer quality metrics for run {metrics.run_id}")

    def save_embedding_drift_metrics(self, metrics: RAIAEmbeddingDriftMetrics) -> None:
        """Save embedding drift metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_embedding_drift_metrics (
                    index_name, kl_divergence, js_divergence, wasserstein_distance,
                    avg_similarity_to_baseline, similarity_distribution_shift,
                    drift_detected, drift_severity, drift_threshold,
                    baseline_period_start, baseline_period_end,
                    current_period_start, current_period_end,
                    samples_analyzed, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.index_name,
                metrics.kl_divergence,
                metrics.js_divergence,
                metrics.wasserstein_distance,
                metrics.avg_similarity_to_baseline,
                metrics.similarity_distribution_shift,
                metrics.drift_detected,
                metrics.drift_severity,
                metrics.drift_threshold,
                metrics.baseline_period_start.isoformat() if metrics.baseline_period_start else None,
                metrics.baseline_period_end.isoformat() if metrics.baseline_period_end else None,
                metrics.current_period_start.isoformat() if metrics.current_period_start else None,
                metrics.current_period_end.isoformat() if metrics.current_period_end else None,
                metrics.samples_analyzed,
                metrics.created_at.isoformat(),
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved embedding drift metrics for index {metrics.index_name}")

    def save_vector_index_health(self, metrics: RAIAVectorIndexHealth) -> None:
        """Save vector index health metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_vector_index_health (
                    index_name, total_documents, total_embeddings, index_size_mb,
                    avg_query_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms,
                    avg_recall_at_10, recall_degradation_pct,
                    last_updated, staleness_hours, pending_updates,
                    memory_usage_mb, cpu_usage_pct, disk_usage_mb,
                    health_status, health_issues, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.index_name,
                metrics.total_documents,
                metrics.total_embeddings,
                metrics.index_size_mb,
                metrics.avg_query_latency_ms,
                metrics.p50_latency_ms,
                metrics.p95_latency_ms,
                metrics.p99_latency_ms,
                metrics.avg_recall_at_10,
                metrics.recall_degradation_pct,
                metrics.last_updated.isoformat(),
                metrics.staleness_hours,
                metrics.pending_updates,
                metrics.memory_usage_mb,
                metrics.cpu_usage_pct,
                metrics.disk_usage_mb,
                metrics.health_status,
                json.dumps(metrics.health_issues) if metrics.health_issues else None,
                metrics.created_at.isoformat(),
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved vector index health for {metrics.index_name}")

    def save_pipeline_metrics(self, metrics: RAIAPipelineMetrics) -> None:
        """Save RAG pipeline metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_pipeline_metrics (
                    run_id, pipeline_name, query_preprocessing_ms, embedding_generation_ms,
                    vector_search_ms, reranking_ms, llm_generation_ms, postprocessing_ms,
                    total_pipeline_ms, stages_completed, stages_failed, failed_stage,
                    embedding_tokens, llm_prompt_tokens, llm_completion_tokens,
                    embedding_cost_usd, llm_cost_usd, total_cost_usd,
                    pipeline_success, quality_score, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.run_id,
                metrics.pipeline_name,
                metrics.query_preprocessing_ms,
                metrics.embedding_generation_ms,
                metrics.vector_search_ms,
                metrics.reranking_ms,
                metrics.llm_generation_ms,
                metrics.postprocessing_ms,
                metrics.total_pipeline_ms,
                metrics.stages_completed,
                metrics.stages_failed,
                metrics.failed_stage,
                metrics.embedding_tokens,
                metrics.llm_prompt_tokens,
                metrics.llm_completion_tokens,
                metrics.embedding_cost_usd,
                metrics.llm_cost_usd,
                metrics.total_cost_usd,
                metrics.pipeline_success,
                metrics.quality_score,
                metrics.created_at.isoformat(),
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved pipeline metrics for run {metrics.run_id}")

    def get_retrieval_metrics_for_run(self, run_id: str) -> list[RAIARetrievalMetrics]:
        """Retrieve all retrieval metrics for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_retrieval_metrics WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIARetrievalMetrics(
                    id=row["id"],
                    run_id=row["run_id"],
                    query=row["query"],
                    retrieved_count=row["retrieved_count"],
                    precision_at_k=row["precision_at_k"],
                    recall_at_k=row["recall_at_k"],
                    mrr=row["mrr"],
                    ndcg=row["ndcg"],
                    retrieval_latency_ms=row["retrieval_latency_ms"],
                    rerank_latency_ms=row["rerank_latency_ms"],
                    total_latency_ms=row["total_latency_ms"],
                    context_relevance_score=row["context_relevance_score"],
                    context_diversity=row["context_diversity"],
                    context_coverage=row["context_coverage"],
                    retrieved_doc_ids=json.loads(row["retrieved_doc_ids"]) if row["retrieved_doc_ids"] else [],
                    relevance_scores=json.loads(row["relevance_scores"]) if row["relevance_scores"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_answer_quality_for_run(self, run_id: str) -> list[RAIAAnswerQualityMetrics]:
        """Retrieve all answer quality metrics for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_answer_quality_metrics WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAAnswerQualityMetrics(
                    id=row["id"],
                    run_id=row["run_id"],
                    query=row["query"],
                    answer=row["answer"],
                    answer_faithfulness=row["answer_faithfulness"],
                    hallucination_score=row["hallucination_score"],
                    citation_accuracy=row["citation_accuracy"],
                    answer_relevance=row["answer_relevance"],
                    answer_completeness=row["answer_completeness"],
                    answer_conciseness=row["answer_conciseness"],
                    context_utilization=row["context_utilization"],
                    context_recall=row["context_recall"],
                    self_contradiction=bool(row["self_contradiction"]) if row["self_contradiction"] is not None else None,
                    context_contradiction=bool(row["context_contradiction"]) if row["context_contradiction"] is not None else None,
                    generation_latency_ms=row["generation_latency_ms"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_embedding_drift_metrics(self, index_name: str, limit: Optional[int] = None) -> list[RAIAEmbeddingDriftMetrics]:
        """Retrieve embedding drift metrics for a vector index."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM raia_embedding_drift_metrics WHERE index_name = ? ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query, (index_name,))
            rows = cursor.fetchall()

            return [
                RAIAEmbeddingDriftMetrics(
                    id=row["id"],
                    index_name=row["index_name"],
                    kl_divergence=row["kl_divergence"],
                    js_divergence=row["js_divergence"],
                    wasserstein_distance=row["wasserstein_distance"],
                    avg_similarity_to_baseline=row["avg_similarity_to_baseline"],
                    similarity_distribution_shift=row["similarity_distribution_shift"],
                    drift_detected=bool(row["drift_detected"]),
                    drift_severity=row["drift_severity"],
                    drift_threshold=row["drift_threshold"],
                    baseline_period_start=datetime.fromisoformat(row["baseline_period_start"]) if row["baseline_period_start"] else None,
                    baseline_period_end=datetime.fromisoformat(row["baseline_period_end"]) if row["baseline_period_end"] else None,
                    current_period_start=datetime.fromisoformat(row["current_period_start"]) if row["current_period_start"] else None,
                    current_period_end=datetime.fromisoformat(row["current_period_end"]) if row["current_period_end"] else None,
                    samples_analyzed=row["samples_analyzed"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_vector_index_health(self, index_name: str, limit: Optional[int] = None) -> list[RAIAVectorIndexHealth]:
        """Retrieve vector index health metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM raia_vector_index_health WHERE index_name = ? ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query, (index_name,))
            rows = cursor.fetchall()

            return [
                RAIAVectorIndexHealth(
                    id=row["id"],
                    index_name=row["index_name"],
                    total_documents=row["total_documents"],
                    total_embeddings=row["total_embeddings"],
                    index_size_mb=row["index_size_mb"],
                    avg_query_latency_ms=row["avg_query_latency_ms"],
                    p50_latency_ms=row["p50_latency_ms"],
                    p95_latency_ms=row["p95_latency_ms"],
                    p99_latency_ms=row["p99_latency_ms"],
                    avg_recall_at_10=row["avg_recall_at_10"],
                    recall_degradation_pct=row["recall_degradation_pct"],
                    last_updated=datetime.fromisoformat(row["last_updated"]),
                    staleness_hours=row["staleness_hours"],
                    pending_updates=row["pending_updates"],
                    memory_usage_mb=row["memory_usage_mb"],
                    cpu_usage_pct=row["cpu_usage_pct"],
                    disk_usage_mb=row["disk_usage_mb"],
                    health_status=row["health_status"],
                    health_issues=json.loads(row["health_issues"]) if row["health_issues"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_pipeline_metrics_for_run(self, run_id: str) -> list[RAIAPipelineMetrics]:
        """Retrieve all pipeline metrics for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_pipeline_metrics WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAPipelineMetrics(
                    id=row["id"],
                    run_id=row["run_id"],
                    pipeline_name=row["pipeline_name"],
                    query_preprocessing_ms=row["query_preprocessing_ms"],
                    embedding_generation_ms=row["embedding_generation_ms"],
                    vector_search_ms=row["vector_search_ms"],
                    reranking_ms=row["reranking_ms"],
                    llm_generation_ms=row["llm_generation_ms"],
                    postprocessing_ms=row["postprocessing_ms"],
                    total_pipeline_ms=row["total_pipeline_ms"],
                    stages_completed=row["stages_completed"],
                    stages_failed=row["stages_failed"],
                    failed_stage=row["failed_stage"],
                    embedding_tokens=row["embedding_tokens"],
                    llm_prompt_tokens=row["llm_prompt_tokens"],
                    llm_completion_tokens=row["llm_completion_tokens"],
                    embedding_cost_usd=row["embedding_cost_usd"],
                    llm_cost_usd=row["llm_cost_usd"],
                    total_cost_usd=row["total_cost_usd"],
                    pipeline_success=bool(row["pipeline_success"]),
                    quality_score=row["quality_score"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    # =================================================================
    # EXPLAINABILITY METHODS
    # =================================================================

    def save_attribution_map(self, attribution_map: RAIAAttributionMap) -> None:
        """Save attribution map for answer explainability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_attribution_maps (
                    run_id, query, answer, attributions,
                    overall_confidence, faithfulness_score, hallucination_score,
                    total_context_tokens, utilized_context_tokens, context_efficiency,
                    unique_sources_used, primary_source, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attribution_map.run_id,
                attribution_map.query,
                attribution_map.answer,
                json.dumps([attr.dict() for attr in attribution_map.attributions]),
                attribution_map.overall_confidence,
                attribution_map.faithfulness_score,
                attribution_map.hallucination_score,
                attribution_map.total_context_tokens,
                attribution_map.utilized_context_tokens,
                attribution_map.context_efficiency,
                attribution_map.unique_sources_used,
                attribution_map.primary_source,
                attribution_map.created_at.isoformat(),
                json.dumps(attribution_map.metadata) if attribution_map.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved attribution map for run {attribution_map.run_id}")

    def save_reasoning_trace(self, reasoning_trace: RAIAReasoningTrace) -> None:
        """Save reasoning trace for process explainability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_reasoning_traces (
                    run_id, trace_type, query, final_answer, steps,
                    total_steps, successful_steps, failed_steps,
                    reasoning_quality_score, logical_consistency,
                    total_latency_ms, bottleneck_step, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reasoning_trace.run_id,
                reasoning_trace.trace_type,
                reasoning_trace.query,
                reasoning_trace.final_answer,
                json.dumps([
                    {
                        **step.dict(),
                        'start_time': step.start_time.isoformat(),
                        'end_time': step.end_time.isoformat()
                    }
                    for step in reasoning_trace.steps
                ]),
                reasoning_trace.total_steps,
                reasoning_trace.successful_steps,
                reasoning_trace.failed_steps,
                reasoning_trace.reasoning_quality_score,
                reasoning_trace.logical_consistency,
                reasoning_trace.total_latency_ms,
                reasoning_trace.bottleneck_step,
                reasoning_trace.created_at.isoformat(),
                json.dumps(reasoning_trace.metadata) if reasoning_trace.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved reasoning trace for run {reasoning_trace.run_id}")

    def save_agent_decision(self, agent_decision: RAIAAgentDecision) -> None:
        """Save agent decision for action explainability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_agent_decisions (
                    run_id, node_name, decision_point,
                    selected_action, selection_rationale, selection_confidence,
                    agent_state, context_used, alternatives_considered,
                    num_alternatives, actual_outcome, outcome_success,
                    created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_decision.run_id,
                agent_decision.node_name,
                agent_decision.decision_point,
                agent_decision.selected_action,
                agent_decision.selection_rationale,
                agent_decision.selection_confidence,
                json.dumps(agent_decision.agent_state),
                json.dumps(agent_decision.context_used),
                json.dumps([alt.dict() for alt in agent_decision.alternatives_considered]),
                agent_decision.num_alternatives,
                agent_decision.actual_outcome,
                agent_decision.outcome_success,
                agent_decision.created_at.isoformat(),
                json.dumps(agent_decision.metadata) if agent_decision.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved agent decision for run {agent_decision.run_id}")

    def get_attribution_maps_for_run(self, run_id: str) -> list[RAIAAttributionMap]:
        """Retrieve all attribution maps for a run."""
        from raia.models_explainability import Attribution

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_attribution_maps WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAAttributionMap(
                    id=row["id"],
                    run_id=row["run_id"],
                    query=row["query"],
                    answer=row["answer"],
                    attributions=[Attribution(**attr) for attr in json.loads(row["attributions"])],
                    overall_confidence=row["overall_confidence"],
                    faithfulness_score=row["faithfulness_score"],
                    hallucination_score=row["hallucination_score"],
                    total_context_tokens=row["total_context_tokens"],
                    utilized_context_tokens=row["utilized_context_tokens"],
                    context_efficiency=row["context_efficiency"],
                    unique_sources_used=row["unique_sources_used"],
                    primary_source=row["primary_source"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_reasoning_traces_for_run(self, run_id: str) -> list[RAIAReasoningTrace]:
        """Retrieve all reasoning traces for a run."""
        from raia.models_explainability import ReasoningStep

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_reasoning_traces WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAReasoningTrace(
                    id=row["id"],
                    run_id=row["run_id"],
                    trace_type=row["trace_type"],
                    query=row["query"],
                    final_answer=row["final_answer"],
                    steps=[
                        ReasoningStep(
                            **{
                                **step,
                                'start_time': datetime.fromisoformat(step['start_time']),
                                'end_time': datetime.fromisoformat(step['end_time'])
                            }
                        )
                        for step in json.loads(row["steps"])
                    ],
                    total_steps=row["total_steps"],
                    successful_steps=row["successful_steps"],
                    failed_steps=row["failed_steps"],
                    reasoning_quality_score=row["reasoning_quality_score"],
                    logical_consistency=row["logical_consistency"],
                    total_latency_ms=row["total_latency_ms"],
                    bottleneck_step=row["bottleneck_step"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_agent_decisions_for_run(self, run_id: str) -> list[RAIAAgentDecision]:
        """Retrieve all agent decisions for a run."""
        from raia.models_explainability import AlternativeAction

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_agent_decisions WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAAgentDecision(
                    id=row["id"],
                    run_id=row["run_id"],
                    node_name=row["node_name"],
                    decision_point=row["decision_point"],
                    selected_action=row["selected_action"],
                    selection_rationale=row["selection_rationale"],
                    selection_confidence=row["selection_confidence"],
                    agent_state=json.loads(row["agent_state"]) if row["agent_state"] else {},
                    context_used=json.loads(row["context_used"]) if row["context_used"] else [],
                    alternatives_considered=[AlternativeAction(**alt) for alt in json.loads(row["alternatives_considered"])] if row["alternatives_considered"] else [],
                    num_alternatives=row["num_alternatives"],
                    actual_outcome=row["actual_outcome"],
                    outcome_success=bool(row["outcome_success"]) if row["outcome_success"] is not None else None,
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    # What-If Analysis Methods

    def save_counterfactual_scenario(self, scenario: RAIACounterfactualScenario) -> None:
        """Save counterfactual scenario for what-if analysis."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_counterfactual_scenarios (
                    run_id, scenario_name, scenario_type,
                    original_config, alternative_config,
                    original_quality, original_latency_ms, original_cost_usd, original_metadata,
                    alternative_quality, alternative_latency_ms, alternative_cost_usd, alternative_metadata,
                    quality_delta, quality_delta_pct,
                    latency_delta_ms, latency_delta_pct,
                    cost_delta_usd, cost_delta_pct,
                    is_improvement, recommendation, recommendation_rationale, confidence,
                    pros, cons, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario.run_id,
                scenario.scenario_name,
                scenario.scenario_type,
                json.dumps(scenario.original_config),
                json.dumps(scenario.alternative_config),
                scenario.original_quality,
                scenario.original_latency_ms,
                scenario.original_cost_usd,
                json.dumps(scenario.original_metadata) if scenario.original_metadata else None,
                scenario.alternative_quality,
                scenario.alternative_latency_ms,
                scenario.alternative_cost_usd,
                json.dumps(scenario.alternative_metadata) if scenario.alternative_metadata else None,
                scenario.quality_delta,
                scenario.quality_delta_pct,
                scenario.latency_delta_ms,
                scenario.latency_delta_pct,
                scenario.cost_delta_usd,
                scenario.cost_delta_pct,
                scenario.is_improvement,
                scenario.recommendation,
                scenario.recommendation_rationale,
                scenario.confidence,
                json.dumps(scenario.pros),
                json.dumps(scenario.cons),
                scenario.created_at.isoformat(),
                json.dumps(scenario.metadata) if scenario.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved counterfactual scenario for run {scenario.run_id}")

    def save_sensitivity_analysis(self, analysis: RAIASensitivityAnalysis) -> None:
        """Save sensitivity analysis results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_sensitivity_analyses (
                    run_id, analysis_name, parameters,
                    most_sensitive_param, least_sensitive_param,
                    optimal_config, expected_improvement,
                    num_simulations, analysis_duration_ms,
                    created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.run_id,
                analysis.analysis_name,
                json.dumps([p.dict() for p in analysis.parameters]),
                analysis.most_sensitive_param,
                analysis.least_sensitive_param,
                json.dumps(analysis.optimal_config),
                analysis.expected_improvement,
                analysis.num_simulations,
                analysis.analysis_duration_ms,
                analysis.created_at.isoformat(),
                json.dumps(analysis.metadata) if analysis.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved sensitivity analysis for run {analysis.run_id}")

    def save_optimization_recommendation(self, recommendation: RAIAOptimizationRecommendation) -> None:
        """Save optimization recommendation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_optimization_recommendations (
                    run_id, recommendation_name, optimization_goal,
                    current_quality, current_latency_ms, current_cost_usd,
                    recommended_changes,
                    expected_quality, expected_latency_ms, expected_cost_usd,
                    quality_improvement_pct, latency_improvement_pct, cost_savings_pct,
                    implementation_difficulty, implementation_steps, estimated_implementation_time,
                    risk_level, risks, mitigation_strategies,
                    priority, priority_rationale,
                    estimated_annual_savings_usd, estimated_roi_pct,
                    created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recommendation.run_id,
                recommendation.recommendation_name,
                recommendation.optimization_goal,
                recommendation.current_quality,
                recommendation.current_latency_ms,
                recommendation.current_cost_usd,
                json.dumps(recommendation.recommended_changes),
                recommendation.expected_quality,
                recommendation.expected_latency_ms,
                recommendation.expected_cost_usd,
                recommendation.quality_improvement_pct,
                recommendation.latency_improvement_pct,
                recommendation.cost_savings_pct,
                recommendation.implementation_difficulty,
                json.dumps(recommendation.implementation_steps),
                recommendation.estimated_implementation_time,
                recommendation.risk_level,
                json.dumps(recommendation.risks),
                json.dumps(recommendation.mitigation_strategies),
                recommendation.priority,
                recommendation.priority_rationale,
                recommendation.estimated_annual_savings_usd,
                recommendation.estimated_roi_pct,
                recommendation.created_at.isoformat(),
                json.dumps(recommendation.metadata) if recommendation.metadata else None
            ))
            conn.commit()
            logger.debug(f"Saved optimization recommendation for run {recommendation.run_id}")

    def get_counterfactual_scenarios_for_run(self, run_id: str) -> list[RAIACounterfactualScenario]:
        """Retrieve all counterfactual scenarios for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_counterfactual_scenarios WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIACounterfactualScenario(
                    id=row["id"],
                    run_id=row["run_id"],
                    scenario_name=row["scenario_name"],
                    scenario_type=row["scenario_type"],
                    original_config=json.loads(row["original_config"]),
                    alternative_config=json.loads(row["alternative_config"]),
                    original_quality=row["original_quality"],
                    original_latency_ms=row["original_latency_ms"],
                    original_cost_usd=row["original_cost_usd"],
                    original_metadata=json.loads(row["original_metadata"]) if row["original_metadata"] else None,
                    alternative_quality=row["alternative_quality"],
                    alternative_latency_ms=row["alternative_latency_ms"],
                    alternative_cost_usd=row["alternative_cost_usd"],
                    alternative_metadata=json.loads(row["alternative_metadata"]) if row["alternative_metadata"] else None,
                    quality_delta=row["quality_delta"],
                    quality_delta_pct=row["quality_delta_pct"],
                    latency_delta_ms=row["latency_delta_ms"],
                    latency_delta_pct=row["latency_delta_pct"],
                    cost_delta_usd=row["cost_delta_usd"],
                    cost_delta_pct=row["cost_delta_pct"],
                    is_improvement=bool(row["is_improvement"]),
                    recommendation=row["recommendation"],
                    recommendation_rationale=row["recommendation_rationale"],
                    confidence=row["confidence"],
                    pros=json.loads(row["pros"]) if row["pros"] else [],
                    cons=json.loads(row["cons"]) if row["cons"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_sensitivity_analyses_for_run(self, run_id: str) -> list[RAIASensitivityAnalysis]:
        """Retrieve all sensitivity analyses for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_sensitivity_analyses WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIASensitivityAnalysis(
                    id=row["id"],
                    run_id=row["run_id"],
                    analysis_name=row["analysis_name"],
                    parameters=[ParameterSensitivity(**p) for p in json.loads(row["parameters"])],
                    most_sensitive_param=row["most_sensitive_param"],
                    least_sensitive_param=row["least_sensitive_param"],
                    optimal_config=json.loads(row["optimal_config"]),
                    expected_improvement=row["expected_improvement"],
                    num_simulations=row["num_simulations"],
                    analysis_duration_ms=row["analysis_duration_ms"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]

    def get_optimization_recommendations_for_run(self, run_id: str) -> list[RAIAOptimizationRecommendation]:
        """Retrieve all optimization recommendations for a run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raia_optimization_recommendations WHERE run_id = ? ORDER BY created_at", (run_id,))
            rows = cursor.fetchall()

            return [
                RAIAOptimizationRecommendation(
                    id=row["id"],
                    run_id=row["run_id"],
                    recommendation_name=row["recommendation_name"],
                    optimization_goal=row["optimization_goal"],
                    current_quality=row["current_quality"],
                    current_latency_ms=row["current_latency_ms"],
                    current_cost_usd=row["current_cost_usd"],
                    recommended_changes=json.loads(row["recommended_changes"]),
                    expected_quality=row["expected_quality"],
                    expected_latency_ms=row["expected_latency_ms"],
                    expected_cost_usd=row["expected_cost_usd"],
                    quality_improvement_pct=row["quality_improvement_pct"],
                    latency_improvement_pct=row["latency_improvement_pct"],
                    cost_savings_pct=row["cost_savings_pct"],
                    implementation_difficulty=row["implementation_difficulty"],
                    implementation_steps=json.loads(row["implementation_steps"]),
                    estimated_implementation_time=row["estimated_implementation_time"],
                    risk_level=row["risk_level"],
                    risks=json.loads(row["risks"]),
                    mitigation_strategies=json.loads(row["mitigation_strategies"]),
                    priority=row["priority"],
                    priority_rationale=row["priority_rationale"],
                    estimated_annual_savings_usd=row["estimated_annual_savings_usd"],
                    estimated_roi_pct=row["estimated_roi_pct"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                )
                for row in rows
            ]
