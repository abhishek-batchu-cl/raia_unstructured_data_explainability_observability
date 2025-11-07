#!/bin/bash

# Script to rename EAEF to RAIA across the entire codebase
# RAIA = Responsible AI Analytics & Agent Evaluation

set -e

echo "🔄 Renaming EAEF to RAIA across the codebase..."
echo ""

# Function to replace in file
replace_in_file() {
    local file=$1
    if [ -f "$file" ]; then
        # macOS compatible sed
        sed -i '' 's/EAEF/RAIA/g' "$file"
        sed -i '' 's/eaef/raia/g' "$file"
        sed -i '' 's/Enterprise Agentic Evaluation Framework/Responsible AI Analytics \& Agent Evaluation/g' "$file"
        echo "  ✓ Updated: $file"
    fi
}

# Update documentation
echo "1️⃣  Updating documentation..."
replace_in_file "README.md"
replace_in_file "START_HERE.txt"
replace_in_file "TUTORIAL.md"
replace_in_file "HOW_IT_WORKS.md"
replace_in_file "GETTING_STARTED.md"
replace_in_file "VERIFICATION.md"
replace_in_file "docs/quickstart.md"
replace_in_file "docs/canonical_metrics.md"
replace_in_file "docs/security_compliance.md"
replace_in_file "docs/deployment_scaling.md"
replace_in_file "docs/testing_strategy.md"
replace_in_file "observability/grafana_dashboard_queries.md"
echo ""

# Rename Python package directory
echo "2️⃣  Renaming Python package..."
if [ -d "sdk/python/eaef" ]; then
    mv sdk/python/eaef sdk/python/raia
    echo "  ✓ Renamed: sdk/python/eaef → sdk/python/raia"
fi
echo ""

# Update Python files
echo "3️⃣  Updating Python imports and code..."
find sdk/python -name "*.py" -type f | while read file; do
    replace_in_file "$file"
done
find services -name "*.py" -type f | while read file; do
    replace_in_file "$file"
done
find tools -name "*.py" -type f | while read file; do
    replace_in_file "$file"
done
echo ""

# Update TypeScript files
echo "4️⃣  Updating TypeScript package..."
if [ -f "sdk/typescript/package.json" ]; then
    sed -i '' 's/"@eaef\/sdk"/"@raia\/sdk"/g' sdk/typescript/package.json
    sed -i '' 's/"name": "eaef"/"name": "raia"/g' sdk/typescript/package.json
    echo "  ✓ Updated: sdk/typescript/package.json"
fi
find sdk/typescript -name "*.ts" -type f | while read file; do
    replace_in_file "$file"
done
echo ""

# Update JSON schema
echo "5️⃣  Updating JSON schemas..."
replace_in_file "schemas/event_schema.json"
replace_in_file "config/metrics_config.json"
echo ""

# Update config files
echo "6️⃣  Updating configuration files..."
find deploy -name "*.yaml" -o -name "*.yml" -type f | while read file; do
    replace_in_file "$file"
done
find observability -name "*.yaml" -o -name "*.yml" -type f | while read file; do
    replace_in_file "$file"
done
replace_in_file "services/ingestion/Dockerfile"
replace_in_file "services/ingestion/docker-compose.yml" 2>/dev/null || true
echo ""

# Update shell scripts
echo "7️⃣  Updating scripts..."
replace_in_file "quickstart.sh"
echo ""

# Update SQL
echo "8️⃣  Updating SQL schemas..."
replace_in_file "services/ingestion/schema.sql"
echo ""

echo "✅ Renaming complete!"
echo ""
echo "Summary of changes:"
echo "  • Package name: eaef → raia"
echo "  • Environment vars: EAEF_* → RAIA_*"
echo "  • Full name: Enterprise Agentic Evaluation Framework → Responsible AI Analytics & Agent Evaluation"
echo ""
echo "Next steps:"
echo "  1. Test the renamed code: ./quickstart.sh"
echo "  2. Update any external references"
echo "  3. Commit changes: git add . && git commit -m 'Rename EAEF to RAIA'"
echo ""
