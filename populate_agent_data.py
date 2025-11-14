"""
Create agent database with test data
"""
import sqlite3
from datetime import datetime
import random

DB_PATH = "agentic_ai_demo.db"

def create_agent_data():
    """Create agent tables and data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create agent executions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raia_agent_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'success',
            steps_completed INTEGER DEFAULT 0,
            total_steps INTEGER DEFAULT 0,
            tools_used TEXT,
            final_output TEXT,
            error_message TEXT,
            execution_time_ms REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert test agents
    agents = ["ResearchAgent", "AnalysisAgent", "SummarizerAgent", "ValidatorAgent"]

    print("Populating agent database...")

    for i in range(10):
        agent_name = agents[i % len(agents)]
        cursor.execute("""
            INSERT INTO raia_agent_executions
            (run_id, agent_name, task, status, steps_completed, total_steps, tools_used,
             final_output, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"run_{i:04d}",
            agent_name,
            f"Task execution {i}",
            random.choice(["success", "success", "success", "error"]),
            random.randint(3, 8),
            random.randint(5, 10),
            "search,analyze,summarize",
            f"Output from {agent_name}",
            random.uniform(500, 3000)
        ))

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM raia_agent_executions")
    count = cursor.fetchone()[0]

    print(f"✅ Created {count} agent executions")
    print(f"✅ Agent database ready at: {DB_PATH}")

    conn.close()

if __name__ == "__main__":
    create_agent_data()
