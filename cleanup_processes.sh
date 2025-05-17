#!/usr/bin/env bash

echo "Cleaning up Lucy AI processes..."

# Find all processes using port 8000
for pid in $(lsof -ti:8000 2>/dev/null); do
    echo "Killing process $pid on port 8000"
    kill -9 $pid 2>/dev/null
done

# Alternative method using ss
if command -v ss &> /dev/null; then
    PORT_PID=$(ss -tlnp | grep ':8000' | grep -oP '(?<=pid=)\d+')
    if [ ! -z "$PORT_PID" ]; then
        echo "Killing process $PORT_PID on port 8000"
        kill -9 $PORT_PID 2>/dev/null
    fi
fi

# Kill all lucy-related python processes
pkill -9 -f "lucy_AI_server"
pkill -9 -f "lucy_AI_mock_client"
pkill -9 -f "streamlit.*lucy"

# Also check for uvicorn if the server uses it
pkill -9 -f "uvicorn.*lucy"

echo "Cleanup complete. Waiting for ports to be released..."
sleep 2

# Check if port is still in use
if ss -tlnp | grep -q ':8000'; then
    echo "Warning: Port 8000 is still in use"
    ss -tlnp | grep ':8000'
else
    echo "Port 8000 is now free"
fi