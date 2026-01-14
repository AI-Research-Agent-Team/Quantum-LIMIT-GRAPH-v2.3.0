#!/bin/bash

# Quantum LIMIT-GRAPH Agent Runner Script
# This script is called by the AgentBeats controller to start the agent

set -e

# Parse command line arguments (AgentBeats standard)
HOST="0.0.0.0"
PORT="8000"
CARD_URL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --card-url)
      CARD_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Export environment variables
export HOST=$HOST
export AGENT_PORT=$PORT
export CARD_URL=$CARD_URL

echo "🚀 Starting Quantum LIMIT-GRAPH Green Agent..."
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Card URL: $CARD_URL"

# Run the agent server
python server.py
