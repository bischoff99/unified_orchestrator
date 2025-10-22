#!/bin/bash
# Launch Master Workflow - One command to automate everything
# Usage: ./launch_workflow.sh "feature description"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ORCHESTRATOR_DIR="$HOME/Developer/projects/unified_orchestrator"
WORKFLOW_DIR="$ORCHESTRATOR_DIR/runs"
SCRIPTS_DIR="$ORCHESTRATOR_DIR/scripts"

# Feature description from command line
if [ "$#" -lt 1 ]; then
    echo -e "${RED}Usage: $0 \"feature description\"${NC}"
    echo "Example: $0 \"implement JWT authentication\""
    exit 1
fi

FEATURE="$1"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RUN_ID="workflow_${TIMESTAMP}"
RUN_DIR="${WORKFLOW_DIR}/${RUN_ID}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          MASTER WORKFLOW ORCHESTRATOR                     ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║ Feature: ${YELLOW}${FEATURE:0:45}${BLUE}║${NC}"
echo -e "${BLUE}║ Run ID:  ${GREEN}${RUN_ID}${BLUE}                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo

# Create run directory
mkdir -p "$RUN_DIR"
echo -e "${GREEN}✓${NC} Created run directory: ${RUN_DIR}"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

check_app() {
    if pgrep -x "$1" > /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is running"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Starting $1..."
        open -a "$1" 2>/dev/null || {
            echo -e "${RED}✗${NC} Could not start $1. Please open it manually."
            return 1
        }
        sleep 2
        echo -e "${GREEN}✓${NC} $1 started"
        return 0
    fi
}

# Check required applications
APPS_OK=true
for app in "Cursor" "Claude" "Perplexity"; do
    check_app "$app" || APPS_OK=false
done

if [ "$APPS_OK" = false ]; then
    echo -e "${RED}Some required applications are not available.${NC}"
    echo "Please ensure Cursor IDE, Claude Desktop, and Perplexity Desktop are installed."
    exit 1
fi

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 is not installed"
    exit 1
else
    echo -e "${GREEN}✓${NC} Python 3 is available"
fi

# Initialize workflow state
echo -e "\n${YELLOW}Initializing workflow...${NC}"
cat > "${RUN_DIR}/config.json" <<EOF
{
  "feature": "$FEATURE",
  "run_id": "$RUN_ID",
  "started_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "orchestrator_dir": "$ORCHESTRATOR_DIR",
  "phases": [
    "research",
    "planning",
    "development",
    "testing",
    "deployment",
    "documentation"
  ]
}
EOF
echo -e "${GREEN}✓${NC} Workflow configuration created"

# Function to execute phase
execute_phase() {
    local phase=$1
    local phase_upper=$(echo "$phase" | tr '[:lower:]' '[:upper:]')
    
    echo -e "\n${BLUE}══════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}PHASE: ${phase_upper}${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
    
    # Log phase start
    echo "$(date): Starting $phase phase" >> "${RUN_DIR}/workflow.log"
    
    # Execute AppleScript for this phase
    osascript "${SCRIPTS_DIR}/coordinate_clients.scpt" "$phase" "$FEATURE" 2>&1 | tee -a "${RUN_DIR}/workflow.log"
    local result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Phase $phase completed successfully"
        echo "$(date): Phase $phase completed" >> "${RUN_DIR}/workflow.log"
        
        # Save phase checkpoint
        cat > "${RUN_DIR}/checkpoint_${phase}.json" <<EOF
{
  "phase": "$phase",
  "status": "completed",
  "completed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
        return 0
    else
        echo -e "${RED}✗${NC} Phase $phase failed"
        echo "$(date): Phase $phase failed with code $result" >> "${RUN_DIR}/workflow.log"
        return $result
    fi
}

# Function to monitor workflow
monitor_workflow() {
    local pid=$1
    local phase=$2
    
    echo -e "${YELLOW}Monitoring $phase phase...${NC}"
    
    while kill -0 $pid 2>/dev/null; do
        # Show progress indicator
        echo -n "."
        sleep 2
    done
    echo
}

# Main workflow execution
echo -e "\n${GREEN}Starting workflow execution...${NC}"
echo -e "${YELLOW}This will coordinate between Cursor, Claude, and Perplexity${NC}"
echo -e "${YELLOW}Please allow the apps to control your screen${NC}"
echo

# Option for manual vs automatic execution
echo -e "${BLUE}Select execution mode:${NC}"
echo "1) Automatic - Run all phases sequentially"
echo "2) Interactive - Confirm before each phase"
echo -n "Choice (1/2): "
read -r mode

PHASES=("research" "planning" "development" "testing" "deployment" "documentation")
PHASE_INDEX=0

# Check for resume
if [ -f "${ORCHESTRATOR_DIR}/runs/.last_workflow" ]; then
    LAST_WORKFLOW=$(cat "${ORCHESTRATOR_DIR}/runs/.last_workflow")
    if [ -d "${WORKFLOW_DIR}/${LAST_WORKFLOW}" ]; then
        echo -e "\n${YELLOW}Found incomplete workflow: ${LAST_WORKFLOW}${NC}"
        echo -n "Resume previous workflow? (y/n): "
        read -r resume
        if [ "$resume" = "y" ]; then
            RUN_DIR="${WORKFLOW_DIR}/${LAST_WORKFLOW}"
            # Find last completed phase
            for i in "${!PHASES[@]}"; do
                if [ -f "${RUN_DIR}/checkpoint_${PHASES[$i]}.json" ]; then
                    PHASE_INDEX=$((i + 1))
                fi
            done
            echo -e "${GREEN}Resuming from phase: ${PHASES[$PHASE_INDEX]}${NC}"
        fi
    fi
fi

# Save current workflow as last
echo "$RUN_ID" > "${ORCHESTRATOR_DIR}/runs/.last_workflow"

# Execute phases
for ((i=PHASE_INDEX; i<${#PHASES[@]}; i++)); do
    phase="${PHASES[$i]}"
    
    if [ "$mode" = "2" ]; then
        echo -e "\n${YELLOW}Ready to execute: ${phase}${NC}"
        echo -n "Continue? (y/n/skip): "
        read -r confirm
        
        if [ "$confirm" = "skip" ]; then
            echo -e "${YELLOW}Skipping $phase phase${NC}"
            continue
        elif [ "$confirm" != "y" ]; then
            echo -e "${RED}Workflow paused at $phase${NC}"
            break
        fi
    fi
    
    # Execute the phase
    if execute_phase "$phase"; then
        # Phase succeeded
        sleep 2
    else
        # Phase failed
        echo -e "${RED}Workflow failed at phase: $phase${NC}"
        echo -n "Retry? (y/n): "
        read -r retry
        
        if [ "$retry" = "y" ]; then
            ((i--))  # Decrement to retry this phase
            continue
        else
            echo -e "${RED}Workflow aborted${NC}"
            exit 1
        fi
    fi
done

# Generate final report
echo -e "\n${YELLOW}Generating workflow report...${NC}"

cat > "${RUN_DIR}/report.md" <<EOF
# Workflow Execution Report

**Feature:** $FEATURE  
**Run ID:** $RUN_ID  
**Started:** $(date -r "${RUN_DIR}/config.json" "+%Y-%m-%d %H:%M:%S")  
**Completed:** $(date "+%Y-%m-%d %H:%M:%S")

## Phase Summary

| Phase | Status | Completed At |
|-------|--------|--------------|
EOF

for phase in "${PHASES[@]}"; do
    if [ -f "${RUN_DIR}/checkpoint_${phase}.json" ]; then
        completed_at=$(grep "completed_at" "${RUN_DIR}/checkpoint_${phase}.json" | cut -d'"' -f4)
        echo "| ${phase^} | ✅ Complete | $completed_at |" >> "${RUN_DIR}/report.md"
    else
        echo "| ${phase^} | ⏭️ Skipped | - |" >> "${RUN_DIR}/report.md"
    fi
done

cat >> "${RUN_DIR}/report.md" <<EOF

## Generated Artifacts

### Research Phase
- Research documents: \`research/\`
- Linear Epic created
- Notion research page created

### Planning Phase
- Technical specification in ChromaDB
- Linear sub-tasks created
- Architecture documented

### Development Phase
- Source code in \`src/features/\`
- Tests in \`tests/\`
- Supermemory patterns saved

### Testing Phase
- Test reports generated
- Coverage analysis complete
- Browser tests recorded

### Deployment Phase
- GitHub PR created
- Deployment to staging
- Slack notification sent

### Documentation Phase
- Notion documentation complete
- Code documentation generated
- Decision log created
- Space updated with learnings

## Logs

Full execution log: \`${RUN_DIR}/workflow.log\`

---
*Generated by Master Workflow Orchestrator*
EOF

echo -e "${GREEN}✓${NC} Report generated: ${RUN_DIR}/report.md"

# Cleanup
rm -f "${ORCHESTRATOR_DIR}/runs/.last_workflow"

# Final summary
echo
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 WORKFLOW COMPLETE! 🎉                     ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║ Feature: ${FEATURE:0:45}║${NC}"
echo -e "${GREEN}║ Report:  ${RUN_DIR}/report.md   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"

# Open report in default editor
echo -e "\n${YELLOW}Opening report...${NC}"
open "${RUN_DIR}/report.md" 2>/dev/null || cat "${RUN_DIR}/report.md"

# Optional: Open Linear, GitHub, and Notion
echo -e "\n${BLUE}Quick Links:${NC}"
echo "• Linear: https://linear.app/workspace"
echo "• GitHub: https://github.com/user/repo"
echo "• Notion: https://notion.so/workspace"
echo "• Perplexity Space: https://www.perplexity.ai/spaces/agentic-workflow-orchestration"

exit 0
