"""
Quick script to populate database with test data for dashboard testing
"""
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "complete_end_to_end_demo.db"

def create_tables_and_data():
    """Create tables and populate with test data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create retrieval metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raia_retrieval_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            query TEXT NOT NULL,
            precision_at_k REAL,
            recall_at_k REAL,
            f1_at_k REAL,
            mrr REAL,
            ndcg_at_k REAL,
            retrieved_count INTEGER,
            relevant_count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create answer quality table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raia_answer_quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            query TEXT NOT NULL,
            answer TEXT,
            faithfulness REAL,
            hallucination_score REAL,
            relevance_score REAL,
            correctness_score REAL,
            completeness_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Generate test data
    queries = [
        "What is machine learning?",
        "Explain neural networks",
        "How does RAG work?",
        "What is vector search?",
        "Describe transformers architecture",
        "What are embeddings?",
        "How to fine-tune LLMs?",
        "What is semantic search?",
        "Explain attention mechanism",
        "What is transfer learning?"
    ]

    print("Populating database with test data...")

    for i in range(20):
        run_id = f"run_{i:04d}"
        query = queries[i % len(queries)]
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat()

        # Insert retrieval metrics
        cursor.execute("""
            INSERT INTO raia_retrieval_metrics
            (run_id, query, precision_at_k, recall_at_k, f1_at_k, mrr, ndcg_at_k,
             retrieved_count, relevant_count, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            query,
            random.uniform(0.7, 0.95),
            random.uniform(0.6, 0.9),
            random.uniform(0.65, 0.92),
            random.uniform(0.7, 1.0),
            random.uniform(0.7, 0.95),
            random.randint(3, 10),
            random.randint(2, 8),
            timestamp
        ))

        # Insert answer quality
        cursor.execute("""
            INSERT INTO raia_answer_quality_metrics
            (run_id, query, answer, faithfulness, hallucination_score, relevance_score,
             correctness_score, completeness_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            query,
            f"This is a test answer for query: {query}",
            random.uniform(0.8, 0.98),
            random.uniform(0.01, 0.1),
            random.uniform(0.75, 0.95),
            random.uniform(0.7, 0.95),
            random.uniform(0.65, 0.9),
            timestamp
        ))

    conn.commit()

    # Verify data
    cursor.execute("SELECT COUNT(*) FROM raia_retrieval_metrics")
    retrieval_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM raia_answer_quality_metrics")
    quality_count = cursor.fetchone()[0]

    print(f"✅ Created {retrieval_count} retrieval metrics")
    print(f"✅ Created {quality_count} answer quality metrics")
    print(f"✅ Database ready at: {DB_PATH}")

    conn.close()

if __name__ == "__main__":
    create_tables_and_data()
