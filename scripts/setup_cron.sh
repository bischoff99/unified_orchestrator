#!/bin/bash
# Setup cron job for nightly profiling

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🕐 Setting up nightly profiling cron job"
echo "=========================================="

# Create cron job entry
CRON_ENTRY="0 2 * * * cd $PROJECT_DIR && source venv/bin/activate && python src/mcp/nightly_profile.py >> logs/nightly_profiling.log 2>&1"

echo "Cron job configuration:"
echo "  Schedule: Daily at 2:00 AM"
echo "  Command: python src/mcp/nightly_profile.py"
echo "  Log: logs/nightly_profiling.log"
echo ""

# Check if cron job already exists
existing=$(crontab -l 2>/dev/null | grep -F "nightly_profile.py" || true)

if [ -n "$existing" ]; then
    echo "⚠️  Cron job already exists:"
    echo "   $existing"
    echo ""
    read -p "Replace existing cron job? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 0
    fi
    
    # Remove existing entry
    crontab -l | grep -v "nightly_profile.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job added successfully!"
echo ""
echo "Verify with: crontab -l | grep nightly_profile"
echo "View logs: tail -f logs/nightly_profiling.log"
echo ""
echo "To remove: crontab -e (then delete the line)"

