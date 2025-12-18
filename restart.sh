#!/bin/bash
# Script to restart the Flask app

PID_FILE=".flask_pid"

# Stop existing instance
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Stopping Flask app (PID: $OLD_PID)..."
        kill "$OLD_PID"
        sleep 2
        # Force kill if still running
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            kill -9 "$OLD_PID" 2>/dev/null
        fi
    fi
    rm -f "$PID_FILE"
fi

# Find and kill any other Flask instances on port 80
PORT_PID=$(lsof -ti:80 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "Found process on port 80 (PID: $PORT_PID), stopping it..."
    kill -9 "$PORT_PID" 2>/dev/null
fi

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Start Flask app
echo "Starting Flask app..."
python src/main.py > logs/app.log 2>&1 &
NEW_PID=$!

echo "$NEW_PID" > "$PID_FILE"
echo "Flask app started (PID: $NEW_PID)"
echo "Log file: logs/app.log"
echo "Webhook log: logs/webhook.log"
echo ""
echo "To view logs:"
echo "  tail -f logs/app.log"
echo "  tail -f logs/webhook.log"
echo ""
echo "To stop:"
echo "  kill $NEW_PID"
