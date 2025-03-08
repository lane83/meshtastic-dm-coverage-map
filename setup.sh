#!/bin/bash
# Setup script for Meshtastic Coverage Map

# Make script executable
chmod +x server.py
chmod +x test_message.py
chmod +x simulate_route.py

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo "To start the server, run: source venv/bin/activate && python server.py"
