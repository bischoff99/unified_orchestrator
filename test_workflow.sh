#!/bin/bash
# Quick Test Script - Verify Workflow System
# This tests the basic workflow without requiring all apps

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     WORKFLOW SYSTEM TEST                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Checking Prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3 available: $(python3 --version)"
else
    echo "✗ Python 3 not found"
    exit 1
fi

# Check scripts exist
echo -e "\n${BLUE}2. Checking Scripts...${NC}"
for script in scripts/launch_workflow.sh scripts/master_workflow.py scripts/coordinate_clients.scpt; do
    if [ -x "$script" ]; then
        echo -e "${GREEN}✓${NC} $script is executable"
    else
        echo "✗ $script not executable or missing"
        exit 1
    fi
done

# Check documentation
echo -e "\n${BLUE}3. Checking Documentation...${NC}"
for doc in START_HERE.md WORKFLOW_QUICKSTART.md COMPLETE_INTEGRATION_SUMMARY.md; do
    if [ -f "$doc" ]; then
        lines=$(wc -l < "$doc")
        echo -e "${GREEN}✓${NC} $doc exists ($lines lines)"
    else
        echo "✗ $doc missing"
        exit 1
    fi
done

# Check MCP config
echo -e "\n${BLUE}4. Checking MCP Configuration...${NC}"
if [ -f ~/.cursor/mcp.json ]; then
    echo -e "${GREEN}✓${NC} ~/.cursor/mcp.json exists"
    # Count servers
    servers=$(grep -c "\"command\":" ~/.cursor/mcp.json 2>/dev/null || echo "0")
    echo -e "${GREEN}✓${NC} Found $servers MCP servers configured"
else
    echo -e "${YELLOW}⚠${NC} ~/.cursor/mcp.json not found (optional)"
fi

# Check ChromaDB directory
echo -e "\n${BLUE}5. Checking Data Directories...${NC}"
if [ -d "memory" ]; then
    echo -e "${GREEN}✓${NC} ChromaDB memory directory exists"
else
    echo -e "${YELLOW}⚠${NC} Creating memory directory..."
    mkdir -p memory
fi

if [ -d "runs" ]; then
    echo -e "${GREEN}✓${NC} Workflow runs directory exists"
else
    echo -e "${YELLOW}⚠${NC} Creating runs directory..."
    mkdir -p runs
fi

# Test Python import
echo -e "\n${BLUE}6. Testing Python Dependencies...${NC}"
python3 -c "import asyncio, json, subprocess; print('✓ Core imports work')" 2>&1 | head -1

# Create test workflow state
echo -e "\n${BLUE}7. Creating Test Workflow...${NC}"
TEST_DIR="runs/test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"

cat > "$TEST_DIR/config.json" <<EOF
{
  "feature": "test workflow verification",
  "run_id": "test_$(date +%Y%m%d_%H%M%S)",
  "started_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "status": "test_complete"
}
EOF

if [ -f "$TEST_DIR/config.json" ]; then
    echo -e "${GREEN}✓${NC} Test workflow created: $TEST_DIR"
else
    echo "✗ Failed to create test workflow"
    exit 1
fi

# Summary
echo
echo "╔════════════════════════════════════════════════════════╗"
echo "║     ALL TESTS PASSED! ✓                                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo
echo -e "${GREEN}Your workflow system is ready to use!${NC}"
echo
echo "Next steps:"
echo "  1. Open START_HERE.md for complete guide"
echo "  2. Run: ./scripts/launch_workflow.sh \"hello world API\""
echo "  3. Configure Perplexity MCP connectors"
echo
echo "Documentation:"
echo "  • START_HERE.md - Complete setup guide"
echo "  • WORKFLOW_QUICKSTART.md - 5-minute quick start"
echo "  • docs/MASTER_WORKFLOW_ORCHESTRATION.md - Full details"
echo

exit 0

