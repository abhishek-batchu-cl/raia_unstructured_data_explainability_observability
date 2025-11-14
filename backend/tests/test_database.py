"""
Tests for Database Module
==========================
"""

import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    DatabaseType,
    DatabaseConfig,
    DatabaseManager,
    QueryBuilder,
    Migrator
)


class TestQueryBuilder:
    """Test SQL query builder."""

    def test_select_basic(self):
        """Test basic SELECT query."""
        query, params = QueryBuilder.select("users")

        assert query == "SELECT * FROM users"
        assert params == ()

    def test_select_with_columns(self):
        """Test SELECT with specific columns."""
        query, params = QueryBuilder.select("users", columns=["id", "name"])

        assert query == "SELECT id, name FROM users"
        assert params == ()

    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        query, params = QueryBuilder.select(
            "users",
            where={"status": "active", "role": "admin"}
        )

        assert "SELECT * FROM users WHERE" in query
        assert "status = ?" in query
        assert "role = ?" in query
        assert params == ("active", "admin")

    def test_select_with_limit_offset(self):
        """Test SELECT with LIMIT and OFFSET."""
        query, params = QueryBuilder.select(
            "users",
            limit=10,
            offset=20
        )

        assert "LIMIT 10" in query
        assert "OFFSET 20" in query

    def test_insert(self):
        """Test INSERT query."""
        query, params = QueryBuilder.insert(
            "users",
            {"name": "John", "email": "john@example.com"}
        )

        assert "INSERT INTO users" in query
        assert "name, email" in query
        assert "VALUES (?, ?)" in query
        assert params == ("John", "john@example.com")

    def test_update(self):
        """Test UPDATE query."""
        query, params = QueryBuilder.update(
            "users",
            {"name": "Jane"},
            where={"id": 123}
        )

        assert "UPDATE users SET" in query
        assert "name = ?" in query
        assert "WHERE id = ?" in query
        assert params == ("Jane", 123)

    def test_delete(self):
        """Test DELETE query."""
        query, params = QueryBuilder.delete(
            "users",
            where={"id": 123}
        )

        assert "DELETE FROM users WHERE id = ?" in query
        assert params == (123,)


class TestDatabaseManager:
    """Test database manager."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name

        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=db_path
        )
        db = DatabaseManager(config)

        # Create test table
        db.execute_update("""
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)

        yield db

        # Cleanup
        os.unlink(db_path)

    def test_execute_insert(self, temp_db):
        """Test INSERT operation."""
        affected = temp_db.execute_update(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("John Doe", "john@example.com")
        )

        assert affected == 1

    def test_execute_select(self, temp_db):
        """Test SELECT operation."""
        # Insert data
        temp_db.execute_update(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("Jane Doe", "jane@example.com")
        )

        # Query data
        results = temp_db.execute_query("SELECT * FROM test_users")

        assert len(results) == 1
        assert results[0]["name"] == "Jane Doe"
        assert results[0]["email"] == "jane@example.com"

    def test_execute_update(self, temp_db):
        """Test UPDATE operation."""
        # Insert data
        temp_db.execute_update(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("John Doe", "john@example.com")
        )

        # Update data
        affected = temp_db.execute_update(
            "UPDATE test_users SET email = ? WHERE name = ?",
            ("newemail@example.com", "John Doe")
        )

        assert affected == 1

        # Verify update
        results = temp_db.execute_query(
            "SELECT email FROM test_users WHERE name = ?",
            ("John Doe",)
        )
        assert results[0]["email"] == "newemail@example.com"

    def test_execute_delete(self, temp_db):
        """Test DELETE operation."""
        # Insert data
        temp_db.execute_update(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("John Doe", "john@example.com")
        )

        # Delete data
        affected = temp_db.execute_update(
            "DELETE FROM test_users WHERE name = ?",
            ("John Doe",)
        )

        assert affected == 1

        # Verify deletion
        results = temp_db.execute_query("SELECT * FROM test_users")
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
