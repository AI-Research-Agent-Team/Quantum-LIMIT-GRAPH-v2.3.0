#!/bin/bash

# Quantum LIMIT-GRAPH Agent Runner Script
# This script is called by the AgentBeats controller to start the agent

set -e

# Set default values if not provided
export HOST=${HOST:-0.0.0.0}
export AGENT_PORT=${AGENT_PORT:-8000}

echo "Starting Quantum LIMIT-GRAPH Green Agent..."
echo "Host: $HOST"
echo "Port: $AGENT_PORT"

# Run the FastAPI application
exec python app.py
