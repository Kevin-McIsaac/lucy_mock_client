#!/usr/bin/env bash

# Script to launch both Lucy AI server and mock client

# Colours for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

echo -e "${GREEN}Starting Lucy AI...${NC}"
echo

# Kill any existing processes first
echo -e "${YELLOW}Checking for existing processes...${NC}"

# Run cleanup script if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/cleanup_processes.sh" ]; then
    echo -e "${YELLOW}Running cleanup script...${NC}"
    "$SCRIPT_DIR/cleanup_processes.sh"
else
    # Fallback to basic cleanup
    pkill -f "python.*lucy_AI_server.py" 2>/dev/null
    pkill -f "streamlit.*lucy_AI_mock_client.py" 2>/dev/null
    sleep 1  # Give processes time to shut down
fi

# Function to activate virtual environment and run a command
activate_venv_and_run() {
    local cmd="$1"
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        eval "$cmd" &
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        eval "$cmd" &
    else
        # Try to run with system python
        echo -e "${YELLOW}No virtual environment found, using system Python...${NC}"
        eval "python3 $cmd" &
    fi
}

# Function to start Lucy AI server
start_lucy_server() {
    echo -e "${YELLOW}Starting Lucy AI server...${NC}"
    cd ~/Projects/lucy-ai
    
    activate_venv_and_run "python lucy_AI_server.py"
    SERVER_PID=$!
    
    echo -e "${GREEN}Lucy AI server started with PID: $SERVER_PID${NC}"
}

# Function to start Mock Client
start_mock_client() {
    echo -e "${YELLOW}Starting Mock Client...${NC}"
    cd ~/Projects/lucy_mock_client
    
    activate_venv_and_run "streamlit run lucy_AI_mock_client.py"
    CLIENT_PID=$!
    
    echo -e "${GREEN}Mock client started with PID: $CLIENT_PID${NC}"
}

# Function to handle shutdown
shutdown() {
    echo
    echo -e "${YELLOW}Shutting down...${NC}"
    
    # Try to kill by PID first
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
    
    # Wait a moment for graceful shutdown
    sleep 1
    
    # Force kill if still running
    kill -9 $SERVER_PID 2>/dev/null
    kill -9 $CLIENT_PID 2>/dev/null
    
    # Also kill by process name as a fallback
    pkill -f "python.*lucy_AI_server.py" 2>/dev/null
    pkill -f "streamlit.*lucy_AI_mock_client.py" 2>/dev/null
    
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Start both services
start_lucy_server
echo
start_mock_client

echo
echo -e "${GREEN}Both components are running!${NC}"
echo -e "${YELLOW}Lucy AI Server PID: $SERVER_PID${NC}"
echo -e "${YELLOW}Mock Client PID: $CLIENT_PID${NC}"
echo
echo "Press Ctrl+C to stop both services"

# Set up trap to handle Ctrl+C
trap shutdown SIGINT

# Wait for both processes
wait $SERVER_PID $CLIENT_PID