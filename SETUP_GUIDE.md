# Quantum LIMIT-GRAPH AgentBeats Setup Guide

Complete guide for preparing and submitting your Quantum LIMIT-GRAPH green agent to the AgentX-AgentBeats Competition.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Setup](#docker-setup)
4. [Testing Your Agent](#testing-your-agent)
5. [Publishing to GitHub Container Registry](#publishing-to-ghcr)
6. [AgentBeats Registration](#agentbeats-registration)
7. [Submitting to Competition](#competition-submission)

## 1. Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11 or higher
- ✅ Docker Desktop installed and running
- ✅ GitHub account with write access to your fork
- ✅ AgentBeats account (register at https://agentbeats.dev)

## 2. Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Quantum-LIMIT-GRAPH-v2.3.0.git
cd Quantum-LIMIT-GRAPH-v2.3.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🧪 Testing Locally

### Step 1: Start the Green Agent (Evaluator)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the green agent
python app.py
```

The green agent will start on `http://localhost:8000`

### Step 2: Run Baseline Purple Agent (in another terminal)

```bash
python baseline_purple_agent.py
```

This starts the baseline purple agent on port 8001.

### Step 3: Test the Evaluation

```python
# test_evaluation.py
import requests
import json

# Purple agent endpoint
PURPLE_AGENT_URL = "http://localhost:8001"
GREEN_AGENT_URL = "http://localhost:8000"

# Test multilingual query
test_queries = [
    "What are recent developments in quantum machine learning?",  # English
    "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?",  # Indonesian
    "量子机器学习的最新进展是什么？",  # Chinese
    "¿Cuáles son los últimos avances en aprendizaje automático cuántico?",  # Spanish
]

async def test_evaluation():
    import aiohttp
    
    for query in queries:
        # Purple agent generates response
        purple_response = await generate_response(query)
        
        # Send to green agent for evaluation
        async with aiohttp.ClientSession() as session:
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "parts": [{"type": "text", "text": query}]
                    },
                    {
                        "role": "agent",
                        "parts": [{"type": "text", "text": purple_response}]
                    }
                ],
                "config": {"test_mode": True}
            }
            
            async with session.post(
                "http://localhost:8000/v1/tasks",
                json=request
            ) as resp:
                result = await resp.json()
                print(f"\n Task ID: {result['task_id']}")
                print(f"Status: {result['status']}")

if __name__ == "__main__":
    print("Starting Baseline Purple Agent on port 8001...")
    print("Green Agent should be running on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8001)
