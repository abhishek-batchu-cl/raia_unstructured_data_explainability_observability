"""
Database Module for RAIA Enterprise
====================================

Supports multiple database backends:
- SQLite (development/demo)
- PostgreSQL (production)

Features:
- Connection pooling
- Async support
- Migration utilities
- Query builders
"""

from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import sqlite3
from enum import Enum

# ============================================================================
# Database Configuration
# ============================================================================

class DatabaseType(Enum):
    """Supported database types."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class DatabaseConfig:
    """Database configuration."""

    def __init__(
        self,
        db_type: DatabaseType = DatabaseType.SQLITE,
        sqlite_path: str = "data/demo_databases/complete_end_to_end_demo.db",
        postgres_url: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10
    ):
        self.db_type = db_type
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url or "postgresql://user:password@localhost:5432/raia"
        self.pool_size = pool_size
        self.max_overflow = max_overflow


# ============================================================================
# SQLite Connection Manager
# ============================================================================

class SQLiteManager:
    """SQLite connection manager."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """Get SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update/insert/delete and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount


# ============================================================================
# PostgreSQL Connection Manager
# ============================================================================

class PostgreSQLManager:
    """PostgreSQL connection manager with connection pooling."""

    def __init__(self, url: str, pool_size: int = 5, max_overflow: int = 10):
        self.url = url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._pool = None

    def _init_pool(self):
        """Initialize connection pool."""
        if self._pool is None:
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.pool import QueuePool

                self._pool = create_engine(
                    self.url,
                    poolclass=QueuePool,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_pre_ping=True,  # Verify connections before using
                )
            except ImportError:
                raise ImportError("PostgreSQL support requires: pip install sqlalchemy psycopg2-binary")

    @contextmanager
    def get_connection(self):
        """Get PostgreSQL connection from pool."""
        self._init_pool()
        conn = self._pool.connect()
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results."""
        self._init_pool()
        with self._pool.connect() as conn:
            result = conn.execute(query, params)
            return [dict(row) for row in result]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update/insert/delete and return affected rows."""
        self._init_pool()
        with self._pool.connect() as conn:
            result = conn.execute(query, params)
            conn.commit()
            return result.rowcount


# ============================================================================
# Unified Database Manager
# ============================================================================

class DatabaseManager:
    """
    Unified database manager supporting multiple backends.

    Usage:
        # SQLite
        db = DatabaseManager(DatabaseType.SQLITE, sqlite_path="data.db")

        # PostgreSQL
        db = DatabaseManager(
            DatabaseType.POSTGRESQL,
            postgres_url="postgresql://user:pass@localhost:5432/raia"
        )

        # Execute query
        results = db.execute_query("SELECT * FROM raia_runs")
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config

        if config.db_type == DatabaseType.SQLITE:
            self._manager = SQLiteManager(config.sqlite_path)
        elif config.db_type == DatabaseType.POSTGRESQL:
            self._manager = PostgreSQLManager(
                config.postgres_url,
                config.pool_size,
                config.max_overflow
            )
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results."""
        return self._manager.execute_query(query, params)

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update and return affected rows."""
        return self._manager.execute_update(query, params)

    def get_connection(self):
        """Get raw connection."""
        return self._manager.get_connection()


# ============================================================================
# Migration Utilities
# ============================================================================

class Migrator:
    """Database migration utilities."""

    @staticmethod
    def create_all_tables(db_manager: DatabaseManager):
        """Create all RAIA tables."""

        tables = [
            # Core execution tables
            """
            CREATE TABLE IF NOT EXISTS raia_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                session_id TEXT,
                agent_name TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Node metrics
            """
            CREATE TABLE IF NOT EXISTS raia_node_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                node_name TEXT,
                node_type TEXT,
                execution_time_ms REAL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                success BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Functional signals
            """
            CREATE TABLE IF NOT EXISTS raia_functional_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                signal_type TEXT,
                tool_name TEXT,
                llm_call_type TEXT,
                input_text TEXT,
                output_text TEXT,
                latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Semantic scores
            """
            CREATE TABLE IF NOT EXISTS raia_semantic_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                dimension TEXT,
                score REAL,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Retrieval metrics
            """
            CREATE TABLE IF NOT EXISTS raia_retrieval_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                query TEXT,
                precision_at_k REAL,
                recall_at_k REAL,
                f1_at_k REAL,
                mrr REAL,
                ndcg_at_k REAL,
                retrieval_latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Answer quality metrics
            """
            CREATE TABLE IF NOT EXISTS raia_answer_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                query TEXT,
                answer TEXT,
                answer_faithfulness REAL,
                hallucination_score REAL,
                answer_relevance REAL,
                answer_completeness REAL,
                generation_latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Vector index health
            """
            CREATE TABLE IF NOT EXISTS raia_vector_index_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_name TEXT,
                total_vectors INTEGER,
                avg_query_latency_ms REAL,
                index_size_mb REAL,
                last_updated TIMESTAMP,
                health_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Pipeline metrics
            """
            CREATE TABLE IF NOT EXISTS raia_pipeline_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                pipeline_type TEXT,
                total_latency_ms REAL,
                num_steps INTEGER,
                success_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Embedding drift metrics
            """
            CREATE TABLE IF NOT EXISTS raia_embedding_drift_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                drift_type TEXT,
                kl_divergence REAL,
                js_divergence REAL,
                wasserstein_distance REAL,
                avg_similarity_to_baseline REAL,
                drift_detected BOOLEAN,
                threshold_used REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Attribution maps
            """
            CREATE TABLE IF NOT EXISTS raia_attribution_maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                answer_span TEXT,
                source_doc_id TEXT,
                confidence REAL,
                answer_start_idx INTEGER,
                answer_end_idx INTEGER,
                source_span TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Reasoning traces
            """
            CREATE TABLE IF NOT EXISTS raia_reasoning_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                trace_type TEXT,
                query TEXT,
                final_answer TEXT,
                total_steps INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Agent decisions
            """
            CREATE TABLE IF NOT EXISTS raia_agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                step_number INTEGER,
                decision_type TEXT,
                reasoning TEXT,
                confidence REAL,
                alternatives_considered INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Counterfactual scenarios
            """
            CREATE TABLE IF NOT EXISTS raia_counterfactual_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                scenario_name TEXT,
                parameter_changed TEXT,
                original_value TEXT,
                new_value TEXT,
                predicted_outcome TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Sensitivity analyses
            """
            CREATE TABLE IF NOT EXISTS raia_sensitivity_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                parameter_name TEXT,
                sensitivity_score REAL,
                impact_description TEXT,
                recommended_range TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Optimization recommendations
            """
            CREATE TABLE IF NOT EXISTS raia_optimization_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                recommendation_type TEXT,
                priority TEXT,
                description TEXT,
                expected_improvement REAL,
                implementation_effort TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]

        for table_sql in tables:
            try:
                db_manager.execute_update(table_sql)
                print(f"✅ Created table")
            except Exception as e:
                print(f"❌ Error creating table: {e}")

        print("✅ All tables created successfully")

    @staticmethod
    def migrate_sqlite_to_postgres(
        sqlite_path: str,
        postgres_url: str
    ):
        """
        Migrate data from SQLite to PostgreSQL.

        Args:
            sqlite_path: Path to SQLite database
            postgres_url: PostgreSQL connection URL
        """
        print("🔄 Starting migration from SQLite to PostgreSQL...")

        # Initialize managers
        sqlite_config = DatabaseConfig(DatabaseType.SQLITE, sqlite_path=sqlite_path)
        sqlite_db = DatabaseManager(sqlite_config)

        postgres_config = DatabaseConfig(DatabaseType.POSTGRESQL, postgres_url=postgres_url)
        postgres_db = DatabaseManager(postgres_config)

        # Create tables in PostgreSQL
        Migrator.create_all_tables(postgres_db)

        # Get all table names
        tables = [
            "raia_runs", "raia_node_metrics", "raia_functional_signals",
            "raia_semantic_scores", "raia_retrieval_metrics",
            "raia_answer_quality_metrics", "raia_vector_index_health",
            "raia_pipeline_metrics", "raia_embedding_drift_metrics",
            "raia_attribution_maps", "raia_reasoning_traces",
            "raia_agent_decisions", "raia_counterfactual_scenarios",
            "raia_sensitivity_analyses", "raia_optimization_recommendations"
        ]

        # Migrate each table
        for table in tables:
            try:
                # Get data from SQLite
                rows = sqlite_db.execute_query(f"SELECT * FROM {table}")

                if rows:
                    print(f"📦 Migrating {len(rows)} rows from {table}...")

                    # Insert into PostgreSQL
                    for row in rows:
                        columns = ', '.join(row.keys())
                        placeholders = ', '.join(['%s'] * len(row))
                        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                        postgres_db.execute_update(query, tuple(row.values()))

                    print(f"✅ Migrated {table}")
                else:
                    print(f"⏭️  Skipping {table} (no data)")

            except Exception as e:
                print(f"❌ Error migrating {table}: {e}")

        print("✅ Migration completed!")


# ============================================================================
# Query Builder
# ============================================================================

class QueryBuilder:
    """SQL query builder for common operations."""

    @staticmethod
    def select(
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None
    ) -> tuple:
        """
        Build SELECT query.

        Returns:
            (query, params) tuple
        """
        # Columns
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"
        params = []

        # WHERE clause
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        # ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"

        # LIMIT and OFFSET
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return query, tuple(params)

    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> tuple:
        """
        Build INSERT query.

        Returns:
            (query, params) tuple
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())

        return query, params

    @staticmethod
    def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> tuple:
        """
        Build UPDATE query.

        Returns:
            (query, params) tuple
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause}"
        params = list(data.values())

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return query, tuple(params)

    @staticmethod
    def delete(table: str, where: Dict[str, Any]) -> tuple:
        """
        Build DELETE query.

        Returns:
            (query, params) tuple
        """
        query = f"DELETE FROM {table}"
        params = []

        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        return query, tuple(params)


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # SQLite example
    sqlite_config = DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        sqlite_path="data/demo_databases/complete_end_to_end_demo.db"
    )
    db = DatabaseManager(sqlite_config)

    # Create tables
    Migrator.create_all_tables(db)

    # Query builder example
    query, params = QueryBuilder.select(
        "raia_runs",
        where={"status": "SUCCESS"},
        order_by="created_at DESC",
        limit=10
    )
    results = db.execute_query(query, params)
    print(f"Found {len(results)} runs")

    # PostgreSQL example (uncomment to use)
    # postgres_config = DatabaseConfig(
    #     db_type=DatabaseType.POSTGRESQL,
    #     postgres_url="postgresql://user:pass@localhost:5432/raia"
    # )
    # postgres_db = DatabaseManager(postgres_config)
    # Migrator.create_all_tables(postgres_db)

    # Migration example (uncomment to use)
    # Migrator.migrate_sqlite_to_postgres(
    #     "data/demo_databases/complete_end_to_end_demo.db",
    #     "postgresql://user:pass@localhost:5432/raia"
    # )
