#!/usr/bin/env bash

# Script to launch both Lucy AI server and mock client

# Colours for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

echo -e "${GREEN}Starting Lucy AI...${NC}"
echo

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
    kill $SERVER_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
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