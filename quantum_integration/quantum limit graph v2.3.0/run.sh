# run.sh
#!/bin/bash

# Parse arguments
HOST=${HOST:-0.0.0.0}
PORT=${AGENT_PORT:-8000}
CARD_URL=${CARD_URL:-""}

while [[ $# -gt 0 ]]; do
  case $1 in
    --host) HOST="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --card-url) CARD_URL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

export HOST=$HOST
export AGENT_PORT=$PORT
export CARD_URL=$CARD_URL

echo "🚀 Starting Quantum LIMIT-GRAPH Green Agent..."
python server.py
