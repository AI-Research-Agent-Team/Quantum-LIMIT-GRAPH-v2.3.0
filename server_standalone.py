"""
Standalone Quantum LIMIT-GRAPH Server
Works without earthshaker package for immediate testing
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Try to import agent, but handle errors gracefully
try:
    from agent import QuantumLimitAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import agent.py: {e}")
    print("ℹ️ Using mock agent implementation")
    AGENT_AVAILABLE = False

# Agent Card
AGENT_CARD = {
    "agent_info": {
        "id": "quantum-limit-graph-evaluator",
        "name": "Quantum LIMIT-GRAPH Benchmark",
        "version": "2.3.0",
        "description": "Multilingual quantum research agent benchmark",
        "vendor": "AI Research Agent Team",
        "license": "Apache-2.0"
    },
    "capabilities": {
        "services": [
            {
                "service_id": "multilingual_evaluation",
                "name": "Multilingual Research Evaluation",
                "input_types": ["text", "json"],
                "output_types": ["json", "metrics"]
            }
        ],
        "supported_protocols": ["A2A"],
        "evaluation_type": "green_agent"
    }
}

# FastAPI app
app = FastAPI(title="Quantum LIMIT-GRAPH", version="2.3.0")

# Pydantic models
class MessagePart(BaseModel):
    type: str
    text: Optional[str] = None
    data: Optional[Dict] = None

class Message(BaseModel):
    role: str
    parts: List[MessagePart]

class TaskRequest(BaseModel):
    messages: List[Message]
    config: Optional[Dict] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    messages: List[Message]
    artifacts: Optional[List[Dict]] = None

# In-memory task storage
tasks_db: Dict[str, Dict] = {}

def create_task_id() -> str:
    """Generate unique task ID"""
    import uuid
    return f"task_{uuid.uuid4().hex[:16]}"

def create_message(text: str, data: Optional[Dict] = None) -> Message:
    """Create a message"""
    parts = [MessagePart(type="text", text=text)]
    if data:
        parts.append(MessagePart(type="data", data=data))
    return Message(role="agent", parts=parts)

# Routes

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Agent card for A2A discovery"""
    return JSONResponse(content=AGENT_CARD)

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "Quantum LIMIT-GRAPH",
        "version": "2.3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_available": AGENT_AVAILABLE
    }

@app.post("/v1/tasks")
async def create_task(request: TaskRequest) -> TaskResponse:
    """Create evaluation task"""
    task_id = create_task_id()
    
    # Extract query and response from messages
    query = ""
    agent_response = ""
    
    for message in request.messages:
        for part in message.parts:
            if part.type == "text" and part.text:
                if message.role == "user":
                    query = part.text
                else:
                    agent_response = part.text
    
    # Store task
    tasks_db[task_id] = {
        "id": task_id,
        "status": "submitted",
        "created_at": datetime.utcnow().isoformat(),
        "query": query,
        "agent_response": agent_response,
        "config": request.config or {},
        "messages": [m.dict() for m in request.messages]
    }
    
    # Start evaluation
    asyncio.create_task(run_evaluation(task_id))
    
    return TaskResponse(
        task_id=task_id,
        status="working",
        messages=[create_message(f"Evaluation task {task_id} started")]
    )

async def run_evaluation(task_id: str):
    """Run evaluation asynchronously"""
    task = tasks_db[task_id]
    task["status"] = "working"
    
    try:
        if AGENT_AVAILABLE:
            # Use real agent
            agent = QuantumLimitAgent()
            result = await agent._evaluate_response(
                query=task["query"],
                response=task["agent_response"],
                expected_lang="en"
            )
        else:
            # Use mock evaluation
            await asyncio.sleep(1)  # Simulate processing
            result = {
                "overall_score": 0.75,
                "passed": True,
                "scores": {
                    "parsing_accuracy": 0.95,
                    "semantic_coherence": 0.70,
                    "hallucination_avoidance": 0.80,
                    "latency_score": 0.75,
                    "quantum_performance": 0.65
                },
                "metrics": {
                    "detected_language": "en",
                    "hallucination_rate": 0.02,
                    "traversal_latency_ms": 85.0
                }
            }
        
        task["results"] = result
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)

@app.get("/v1/tasks/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    """Get task status"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    messages = []
    artifacts = None
    
    if task["status"] == "completed" and "results" in task:
        results = task["results"]
        
        text = f"""
Quantum LIMIT-GRAPH Evaluation Results

Overall Score: {results['overall_score']:.2f}
Status: {"PASSED" if results.get('passed') else "FAILED"}

Component Scores:
"""
        for key, value in results.get('scores', {}).items():
            text += f"- {key}: {value:.2f}\n"
        
        messages = [create_message(text, data=results)]
        artifacts = [{"type": "evaluation_results", "data": results}]
        
    elif task["status"] == "failed":
        messages = [create_message(f"Evaluation failed: {task.get('error', 'Unknown')}")]
    else:
        messages = [create_message(f"Task is {task['status']}")]
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        messages=messages,
        artifacts=artifacts
    )

@app.get("/v1/tasks")
async def list_tasks(limit: int = 100) -> Dict[str, Any]:
    """List all tasks"""
    tasks_list = list(tasks_db.values())[-limit:]
    return {
        "tasks": tasks_list,
        "total": len(tasks_db),
        "limit": limit
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Quantum LIMIT-GRAPH",
        "version": "2.3.0",
        "status": "running",
        "agent_available": AGENT_AVAILABLE,
        "endpoints": {
            "agent_card": "/.well-known/agent-card.json",
            "health": "/health",
            "create_task": "POST /v1/tasks",
            "get_task": "GET /v1/tasks/{task_id}",
            "list_tasks": "GET /v1/tasks"
        }
    }

def main():
    """Main entry point"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    
    print("=" * 60)
    print("🚀 Quantum LIMIT-GRAPH Standalone Server")
    print("=" * 60)
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Agent Available: {'✅' if AGENT_AVAILABLE else '⚠️ Using mock'}")
    print(f"   Agent Card: http://{host}:{port}/.well-known/agent-card.json")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
