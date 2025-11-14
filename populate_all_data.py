"""
Comprehensive script to populate all RAIA tables with realistic demo data
"""
import sqlite3
from datetime import datetime, timedelta
import random
import json

# Database paths
DB_PATH = "complete_end_to_end_demo.db"
AGENT_DB_PATH = "agentic_ai_demo.db"

def create_comprehensive_data():
    """Create comprehensive test data for all RAIA tables"""
    print("="*80)
    print("  Populating RAIA Database with Comprehensive Demo Data")
    print("="*80)
    print()

    # Connect to main database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sample queries for different domains
    queries = [
        "What is machine learning and how does it work?",
        "Explain the difference between supervised and unsupervised learning",
        "How do neural networks process information?",
        "What are the key components of a RAG system?",
        "Describe the transformer architecture in detail",
        "What is vector search and why is it important?",
        "How does semantic search differ from keyword search?",
        "Explain the attention mechanism in transformers",
        "What are embeddings and how are they created?",
        "How to fine-tune large language models effectively?",
        "What is transfer learning in deep learning?",
        "Describe different types of neural network architectures",
        "How does backpropagation work in training neural networks?",
        "What are the challenges in deploying ML models to production?",
        "Explain gradient descent and its variants",
    ]

    # Sample answers
    answers_template = [
        "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed...",
        "The main difference between supervised and unsupervised learning lies in the use of labeled data...",
        "Neural networks process information through interconnected layers of nodes, mimicking the human brain's structure...",
        "A RAG (Retrieval-Augmented Generation) system combines information retrieval with language generation...",
        "The transformer architecture, introduced in the 'Attention is All You Need' paper, revolutionized NLP...",
    ]

    print("📊 Creating tables and populating data...")

    # Create semantic scores table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raia_semantic_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            query TEXT NOT NULL,
            answer TEXT,
            semantic_similarity REAL,
            coherence_score REAL,
            fluency_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Clear existing data (safe delete with IF EXISTS check)
    cursor.execute("DELETE FROM raia_retrieval_metrics WHERE 1=1")
    cursor.execute("DELETE FROM raia_answer_quality_metrics WHERE 1=1")
    cursor.execute("DELETE FROM raia_semantic_scores WHERE 1=1")

    # Insert 50 comprehensive runs
    run_count = 50
    for i in range(run_count):
        run_id = f"run_{i:05d}"
        query = queries[i % len(queries)]
        timestamp = (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat()  # Last 7 days

        # Retrieval metrics
        precision = random.uniform(0.65, 0.98)
        recall = random.uniform(0.60, 0.95)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        cursor.execute("""
            INSERT INTO raia_retrieval_metrics
            (run_id, query, precision_at_k, recall_at_k, f1_at_k, mrr, ndcg_at_k,
             retrieved_count, relevant_count, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, query,
            round(precision, 4),
            round(recall, 4),
            round(f1, 4),
            random.uniform(0.7, 1.0),
            random.uniform(0.75, 0.98),
            random.randint(5, 15),
            random.randint(3, 10),
            timestamp
        ))

        # Answer quality
        faithfulness = random.uniform(0.80, 0.98)
        hallucination = random.uniform(0.01, 0.15)

        cursor.execute("""
            INSERT INTO raia_answer_quality_metrics
            (run_id, query, answer, faithfulness, hallucination_score, relevance_score,
             correctness_score, completeness_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, query,
            answers_template[i % len(answers_template)],
            round(faithfulness, 4),
            round(hallucination, 4),
            random.uniform(0.75, 0.96),
            random.uniform(0.70, 0.95),
            random.uniform(0.68, 0.92),
            timestamp
        ))

        # Semantic scores
        cursor.execute("""
            INSERT INTO raia_semantic_scores
            (run_id, query, answer, semantic_similarity, coherence_score, fluency_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, query,
            answers_template[i % len(answers_template)],
            random.uniform(0.75, 0.96),
            random.uniform(0.80, 0.98),
            random.uniform(0.82, 0.98),
            timestamp
        ))

    conn.commit()

    # Verify main database
    cursor.execute("SELECT COUNT(*) FROM raia_retrieval_metrics")
    retrieval_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM raia_answer_quality_metrics")
    quality_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM raia_semantic_scores")
    semantic_count = cursor.fetchone()[0]

    print(f"  ✅ Created {retrieval_count} retrieval metrics")
    print(f"  ✅ Created {quality_count} answer quality metrics")
    print(f"  ✅ Created {semantic_count} semantic scores")
    print()

    conn.close()

    # Populate agent database
    print("🤖 Creating agent data...")
    conn_agent = sqlite3.connect(AGENT_DB_PATH)
    cursor_agent = conn_agent.cursor()

    # Clear existing
    cursor_agent.execute("DELETE FROM raia_agent_executions")

    agents = [
        "ResearchAgent",
        "AnalysisAgent",
        "SummarizerAgent",
        "ValidatorAgent",
        "PlannerAgent"
    ]

    tasks = [
        "Research machine learning fundamentals",
        "Analyze transformer architecture",
        "Summarize research papers",
        "Validate model outputs",
        "Plan multi-step workflow",
        "Execute data analysis pipeline",
        "Generate comprehensive report",
        "Review and critique results"
    ]

    # Create 30 agent executions
    for i in range(30):
        run_id = f"run_{i:05d}"
        agent_name = agents[i % len(agents)]
        task = tasks[i % len(tasks)]
        status = random.choices(["success", "error"], weights=[0.9, 0.1])[0]

        cursor_agent.execute("""
            INSERT INTO raia_agent_executions
            (run_id, agent_name, task, status, steps_completed, total_steps, tools_used,
             final_output, error_message, execution_time_ms, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            agent_name,
            task,
            status,
            random.randint(5, 12),
            random.randint(8, 15),
            json.dumps(["search", "analyze", "summarize", "validate"][:random.randint(2, 4)]),
            f"Successfully completed {task}" if status == "success" else None,
            "Unexpected error in execution" if status == "error" else None,
            random.uniform(800, 5000),
            (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat()
        ))

    conn_agent.commit()

    cursor_agent.execute("SELECT COUNT(*) FROM raia_agent_executions")
    agent_count = cursor_agent.fetchone()[0]

    print(f"  ✅ Created {agent_count} agent executions")
    print(f"  ✅ Agent types: {', '.join(agents)}")
    print()

    conn_agent.close()

    # Summary
    print("="*80)
    print("  ✅ Database Population Complete!")
    print("="*80)
    print(f"  📊 Total Runs: {run_count}")
    print(f"  📈 Retrieval Metrics: {retrieval_count}")
    print(f"  ✅ Answer Quality: {quality_count}")
    print(f"  🔍 Semantic Scores: {semantic_count}")
    print(f"  🤖 Agent Executions: {agent_count}")
    print("="*80)
    print()
    print("🎉 Your dashboard is now fully populated with demo data!")
    print("   Open http://localhost:5173/enterprise to see the results")
    print()

if __name__ == "__main__":
    create_comprehensive_data()
