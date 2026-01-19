# baseline_purple_agent/simple_agent.py
"""Simple purple agent for testing"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/.well-known/agent-card.json")
def agent_card():
    return {
        "agent_info": {
            "id": "baseline-test-agent",
            "name": "Baseline Test Agent",
            "version": "1.0.0"
        }
    }

@app.post("/v1/tasks")
async def create_task(request: dict):
    # Extract query
    query = ""
    for msg in request.get("messages", []):
        for part in msg.get("parts", []):
            if part.get("type") == "text":
                query = part.get("text", "")
    
    # Simple response
    response = f"I received your query: {query}"
    
    return {
        "task_id": "test_123",
        "status": "completed",
        "messages": [
            {
                "role": "agent",
                "parts": [{"type": "text", "text": response}]
            }
        ]
    }

@app.get("/v1/tasks/{task_id}")
async def get_task(task_id: str):
    return {
        "task_id": task_id,
        "status": "completed",
        "messages": [
            {
                "role": "agent",
                "parts": [{"type": "text", "text": "Test response"}]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
