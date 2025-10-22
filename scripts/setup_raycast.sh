#!/bin/bash
# Setup Raycast Pro commands for unified_orchestrator

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RAYCAST_DIR="$HOME/.config/raycast/scripts"

echo "🚀 Setting up Raycast Pro commands for unified_orchestrator"
echo ""

# Create Raycast scripts directory if it doesn't exist
mkdir -p "$RAYCAST_DIR"

echo "📁 Raycast scripts directory: $RAYCAST_DIR"
echo ""

# Create commands
echo "Creating Raycast commands..."
echo ""

# 1. Run Orchestrator
cat > "$RAYCAST_DIR/orchestrator-run.sh" << 'EOF'
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Run Orchestrator
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 🚀
# @raycast.argument1 { "type": "text", "placeholder": "Spec file", "optional": false }

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
orchestrator run "$1"
EOF
chmod +x "$RAYCAST_DIR/orchestrator-run.sh"
echo "✅ Created: orchestrator-run.sh"

# 2. Show Latest Run
cat > "$RAYCAST_DIR/orchestrator-show-latest.sh" << 'EOF'
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Show Latest Run
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 📊

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
LATEST=$(ls -t runs/ 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
    echo "No runs found"
    exit 1
fi
orchestrator show "$LATEST"
EOF
chmod +x "$RAYCAST_DIR/orchestrator-show-latest.sh"
echo "✅ Created: orchestrator-show-latest.sh"

# 3. Open in Cursor
cat > "$RAYCAST_DIR/orchestrator-open-cursor.sh" << 'EOF'
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Open Latest in Cursor
# @raycast.mode silent
# @raycast.packageName unified_orchestrator
# @raycast.icon 💻

cd ~/Developer/projects/unified_orchestrator
LATEST=$(ls -t runs/ 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then
    echo "No runs found"
    exit 1
fi
cursor "runs/$LATEST/outputs"
EOF
chmod +x "$RAYCAST_DIR/orchestrator-open-cursor.sh"
echo "✅ Created: orchestrator-open-cursor.sh"

# 4. Query Memory
cat > "$RAYCAST_DIR/orchestrator-query-memory.sh" << 'EOF'
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Query Vector Memory
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 🧠
# @raycast.argument1 { "type": "text", "placeholder": "Query", "optional": false }

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate

python -c "
from src.utils.vector_store import VectorMemory
m = VectorMemory()
results = m.query('$1', k=5)
print(f'Found {len(results)} results:\n')
for i, r in enumerate(results, 1):
    print(f'{i}. {r[\"id\"]}')
    print(f'   {r[\"document\"][:200]}...\n')
"
EOF
chmod +x "$RAYCAST_DIR/orchestrator-query-memory.sh"
echo "✅ Created: orchestrator-query-memory.sh"

# 5. Ingest from Clipboard
cat > "$RAYCAST_DIR/orchestrator-ingest-clipboard.sh" << 'EOF'
#!/bin/bash

# @raycast.schemaVersion 1
# @raycast.title Ingest from Clipboard
# @raycast.mode fullOutput
# @raycast.packageName unified_orchestrator
# @raycast.icon 📋

cd ~/Developer/projects/unified_orchestrator
source venv/bin/activate
python scripts/ingest_from_clipboard.py --collection research
EOF
chmod +x "$RAYCAST_DIR/orchestrator-ingest-clipboard.sh"
echo "✅ Created: orchestrator-ingest-clipboard.sh"

echo ""
echo "=" * 60
echo "✅ Raycast commands installed!"
echo ""
echo "📖 Usage:"
echo "  1. Open Raycast (Cmd+Space or Opt+Space)"
echo "  2. Type 'orchestrator' to see available commands"
echo "  3. Select a command and provide arguments"
echo ""
echo "Available commands:"
echo "  • Run Orchestrator - Generate code from spec file"
echo "  • Show Latest Run - View most recent orchestrator run"
echo "  • Open Latest in Cursor - Open generated code in Cursor IDE"
echo "  • Query Vector Memory - Search agent memory"
echo "  • Ingest from Clipboard - Save clipboard to ChromaDB"
echo ""
echo "🎯 Next steps:"
echo "  1. Open Raycast"
echo "  2. Search for 'Run Orchestrator'"
echo "  3. Enter spec file: examples/tiny_spec.yaml"
echo ""
