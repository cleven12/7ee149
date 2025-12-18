#!/bin/bash
# Check bot status and show quick info

echo "=== WhatsApp Bot Status ==="
echo ""

# Check if Flask is running
PID_FILE=".flask_pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✓ Flask app is running (PID: $PID)"
    else
        echo "✗ Flask app not running (stale PID file)"
        rm -f "$PID_FILE"
    fi
else
    echo "✗ Flask app not running"
fi

# Check port 80
PORT_PID=$(lsof -ti:80 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "✓ Port 80 is in use (PID: $PORT_PID)"
else
    echo "✗ Port 80 is free"
fi

echo ""

# Show conversation files
CONV_COUNT=$(find data/conversations -name "*.json" 2>/dev/null | wc -l)
echo "Conversations stored: $CONV_COUNT"

# Show log sizes
if [ -f "logs/webhook.log" ]; then
    LOG_SIZE=$(du -h logs/webhook.log | cut -f1)
    LOG_LINES=$(wc -l < logs/webhook.log)
    echo "Webhook log: $LOG_SIZE ($LOG_LINES lines)"
fi

if [ -f "logs/app.log" ]; then
    APP_SIZE=$(du -h logs/app.log | cut -f1)
    echo "App log: $APP_SIZE"
fi

echo ""
echo "Commands:"
echo "  ./restart.sh    - Restart the bot"
echo "  ./test_bot.sh   - Run tests"
echo "  tail -f logs/webhook.log - Watch logs"
