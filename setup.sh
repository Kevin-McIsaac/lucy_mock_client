#!/bin/bash

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Setup complete! To run the app:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the app: streamlit run lucy_AI_mock_client.py"
