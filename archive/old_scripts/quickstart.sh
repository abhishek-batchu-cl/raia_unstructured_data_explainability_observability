#!/bin/bash
# RAIA Quick Start Script
# Run this to see RAIA in action in under 2 minutes!

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                         RAIA QUICK START                                   ║"
echo "║         Responsible AI Analytics & Agent Evaluation                        ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version || { echo "❌ Python 3.10+ required"; exit 1; }
echo "✅ Python OK"
echo ""

# Install RAIA
echo "📦 Installing RAIA..."
pip3 install -e . > /dev/null 2>&1 || { echo "❌ Installation failed"; exit 1; }
echo "✅ RAIA installed"
echo ""

# Clean up any existing demo databases
echo "🧹 Cleaning up old demo databases..."
rm -f demo_complete.db realistic_rag_eval.db demo_explainability.db demo_whatif.db
echo "✅ Cleanup complete"
echo ""

# Run the complete demo
echo "════════════════════════════════════════════════════════════════════════════"
echo "                      RUNNING COMPLETE DEMO                                  "
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "This demonstrates:"
echo "  • RAG evaluation (retrieval, answer quality, pipeline metrics)"
echo "  • Explainability (attribution tracking, reasoning traces)"
echo "  • What-If analysis (counterfactual scenarios)"
echo "  • Comparison & Reporting (multi-run benchmarking)"
echo ""
echo "Press ENTER to continue..."
read

python3 demo_complete.py

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "                           DEMO COMPLETE!                                    "
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Generated database: demo_complete.db"
echo ""
echo "What's next?"
echo ""
echo "1️⃣  Run realistic RAG evaluation:"
echo "   python3 examples/realistic_rag_evaluation.py"
echo ""
echo "2️⃣  Explore explainability features:"
echo "   python3 demo_explainability.py"
echo ""
echo "3️⃣  Try what-if analysis:"
echo "   python3 demo_whatif.py"
echo ""
echo "4️⃣  Query the database:"
echo "   sqlite3 demo_complete.db"
echo "   > SELECT run_id, avg_quality FROM raia_runs;"
echo ""
echo "5️⃣  Read the documentation:"
echo "   cat QUICKSTART.md"
echo ""
echo "6️⃣  Integrate with your RAG system:"
echo "   from raia import RAIARAGInspector, SQLiteRAIAStorage"
echo "   storage = SQLiteRAIAStorage(\"my_rag.db\")"
echo "   inspector = RAIARAGInspector(storage=storage)"
echo ""
echo "📖 Full documentation: README.md"
echo "🐛 Issues: https://github.com/yourusername/raia/issues"
echo ""
echo "✅ RAIA is ready to use!"
echo ""
