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

from .base import BaseRAIAStorage
from ..models import RAIAAgentRun, RAIANodeMetrics, RAIAFunctionalSignal, RAIASemanticScore


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
                    metadata TEXT
                )
            """)

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

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_metrics_run_id ON raia_node_metrics(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_run_id ON raia_functional_signals(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_run_id ON raia_semantic_scores(run_id)")

            conn.commit()

    def save_run(self, run: RAIAAgentRun) -> None:
        """Save a new agent run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO raia_runs (
                    run_id, session_id, agent_name, graph_name, start_time, end_time,
                    status, total_latency_ms, total_tokens_prompt, total_tokens_completion,
                    total_cost_usd, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
