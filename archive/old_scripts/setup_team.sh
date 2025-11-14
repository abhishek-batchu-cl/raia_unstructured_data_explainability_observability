#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║                   RAIA Team Setup Script                           ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PY_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3.9+ required but not found${NC}"
    echo "   Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check pip
echo ""
echo "2. Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ pip $PIP_VERSION found${NC}"
else
    echo -e "${RED}❌ pip not found${NC}"
    echo "   Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install dependencies
echo ""
echo "3. Installing RAIA dependencies..."
echo -e "${YELLOW}   This may take a few minutes...${NC}"

if pip3 install -e . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Installation failed${NC}"
    echo "   Trying with --user flag..."
    if pip3 install --user -e .; then
        echo -e "${GREEN}✅ Dependencies installed with --user flag${NC}"
    else
        echo -e "${RED}❌ Installation failed. Please check errors above.${NC}"
        exit 1
    fi
fi

# Test installation
echo ""
echo "4. Testing RAIA installation..."
if python3 -c "import raia; print('RAIA version:', raia.__version__ if hasattr(raia, '__version__') else 'development')" 2>/dev/null; then
    echo -e "${GREEN}✅ RAIA imported successfully${NC}"
else
    echo -e "${RED}❌ RAIA import failed${NC}"
    exit 1
fi

# Run quick demo
echo ""
echo "5. Running quick demonstration..."
echo -e "${YELLOW}   Computing actual metrics from simulated RAG pipeline...${NC}"
echo ""

if python3 demo_realistic_computed_metrics.py > /tmp/raia_demo_output.txt 2>&1; then
    echo -e "${GREEN}✅ Demo completed successfully!${NC}"
    echo ""
    echo "Sample output:"
    tail -15 /tmp/raia_demo_output.txt
else
    echo -e "${RED}❌ Demo failed${NC}"
    echo "Output:"
    cat /tmp/raia_demo_output.txt
    exit 1
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║                   ✅ Setup Complete!                               ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Generated database: realistic_computed_demo.db"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "  1. Explore the realistic demo:"
echo "     python3 demo_realistic_computed_metrics.py"
echo ""
echo "  2. Run the complete feature demo:"
echo "     python3 demo_complete_all_features.py"
echo ""
echo "  3. Query the database:"
echo "     sqlite3 realistic_computed_demo.db"
echo "     SELECT * FROM raia_retrieval_metrics;"
echo ""
echo "  4. Analyze metrics:"
echo "     python3 tools/analyze_demo_logs.py realistic_computed_demo.db"
echo ""
echo "  5. Read documentation:"
echo "     • README.md - Main overview"
echo "     • FEATURES.md - Complete feature list"
echo "     • DRIFT_DETECTION_SUMMARY.md - Embedding drift details"
echo "     • DOCKER_TROUBLESHOOTING.md - Docker help"
echo ""
echo "❓ Having issues? Check DOCKER_TROUBLESHOOTING.md"
echo ""
