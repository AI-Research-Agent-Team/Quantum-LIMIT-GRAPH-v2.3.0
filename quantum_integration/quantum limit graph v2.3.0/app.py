"""
Quantum LIMIT-GRAPH Green Agent for AgentX-AgentBeats Competition
A2A-compliant evaluator agent for multilingual AI research benchmarking
"""

import os
import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import Quantum LIMIT-GRAPH modules
from quantum_integration.multilingual_parser import parse_query, detect_language
from quantum_integration.quantum_traversal import traverse_graph, get_traversal_metrics
from quantum_integration.ace_context_router import route_context
from quantum_integration.repair_edit_stream import apply_edits, detect_hallucinations

# Initialize FastAPI app
app = FastAPI(title="Quantum LIMIT-GRAPH Evaluator", version="2.3.0")

# Task storage (in-memory for simplicity)
tasks_db: Dict[str, Dict] = {}

# Agent Card for A2A protocol
AGENT_CARD = {
    "agent_info": {
        "id": "quantum-limit-graph-evaluator",
        "name": "Quantum LIMIT-GRAPH Benchmark",
        "version": "2.3.0",
        "description": "Multilingual quantum research agent benchmark for evaluating AI agents on semantic graph traversal, context routing, and hallucination detection",
        "vendor": "AI Research Agent Team",
        "license": "Apache-2.0"
    },
    "capabilities": {
        "services": [
            {
                "service_id": "multilingual_evaluation",
                "name": "Multilingual Research Evaluation",
                "description": "Evaluates agent performance on multilingual queries across 15+ languages",
                "input_types": ["text", "json"],
                "output_types": ["json", "metrics"],
                "parameters": {
                    "supported_languages": ["en", "es", "fr", "de", "zh", "ja", "ko", "ar", "hi", "id", "pt", "ru", "vi", "th", "tr"],
                    "evaluation_metrics": ["accuracy", "latency", "semantic_coherence", "hallucination_rate"]
                }
            },
            {
                "service_id": "quantum_traversal_eval",
                "name": "Quantum Graph Traversal Assessment",
                "description": "Evaluates quantum vs classical traversal performance",
                "input_types": ["graph", "query"],
                "output_types": ["metrics", "comparison"]
            }
        ],
        "supported_protocols": ["HTTP", "A2A"],
        "security_features": ["TLS"],
        "evaluation_type": "green_agent"
    },
    "technical_specs": {
        "runtime_environment": "Python 3.11+",
        "resource_requirements": {
            "cpu": "2 cores",
            "memory": "4GB",
            "disk": "10GB"
        }
    },
    "endpoints": {
        "agent_card": "/.well-known/agent-card.json",
        "tasks_create": "/v1/tasks",
        "tasks_send": "/v1/tasks/{task_id}/messages",
        "tasks_get": "/v1/tasks/{task_id}",
        "tasks_list": "/v1/tasks"
    }
}

# Pydantic models for A2A protocol
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
    metrics: Optional[Dict] = None

# Helper functions
def create_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:16]}"

def create_response_message(text: str, data: Optional[Dict] = None) -> Message:
    """Create a response message"""
    parts = [MessagePart(type="text", text=text)]
    if data:
        parts.append(MessagePart(type="data", data=data))
    return Message(role="agent", parts=parts)

async def evaluate_agent_response(query: str, agent_response: str, config: Dict) -> Dict[str, Any]:
    """
    Main evaluation logic for Quantum LIMIT-GRAPH benchmark
    
    This function evaluates the purple agent's response on:
    1. Multilingual parsing accuracy
    2. Semantic coherence
    3. Hallucination detection
    4. Context routing quality
    5. Latency and performance
    """
    evaluation_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "agent_response": agent_response,
        "scores": {},
        "metrics": {},
        "passed": False
    }
    
    try:
        # 1. Language detection and parsing
        detected_lang = detect_language(query)
        tokens = parse_query(query, lang=detected_lang)
        evaluation_results["detected_language"] = detected_lang
        evaluation_results["metrics"]["parsing_success"] = len(tokens) > 0
        
        # 2. Context routing evaluation
        context = route_context(tokens)
        evaluation_results["metrics"]["context_layers_used"] = len(context.get("layers", []))
        
        # 3. Quantum traversal (if applicable)
        traversal_metrics = await asyncio.to_thread(get_traversal_metrics, context)
        evaluation_results["metrics"]["traversal_latency_ms"] = traversal_metrics.get("latency_ms", 0)
        evaluation_results["metrics"]["quantum_speedup"] = traversal_metrics.get("speedup_factor", 1.0)
        
        # 4. Hallucination detection on agent response
        hallucinations = detect_hallucinations(agent_response, context)
        hallucination_rate = len(hallucinations) / max(len(agent_response.split()), 1)
        evaluation_results["metrics"]["hallucination_rate"] = hallucination_rate
        evaluation_results["metrics"]["hallucinations_detected"] = len(hallucinations)
        
        # 5. Semantic coherence scoring (simplified)
        coherence_score = calculate_coherence_score(query, agent_response, context)
        evaluation_results["scores"]["coherence"] = coherence_score
        
        # 6. Overall scoring
        scores = {
            "parsing_accuracy": 1.0 if evaluation_results["metrics"]["parsing_success"] else 0.0,
            "semantic_coherence": coherence_score,
            "hallucination_avoidance": max(0.0, 1.0 - hallucination_rate * 10),
            "latency_score": calculate_latency_score(traversal_metrics.get("latency_ms", 100)),
            "quantum_performance": min(1.0, traversal_metrics.get("speedup_factor", 1.0) / 2.0)
        }
        
        evaluation_results["scores"] = scores
        evaluation_results["overall_score"] = sum(scores.values()) / len(scores)
        evaluation_results["passed"] = evaluation_results["overall_score"] >= 0.6
        
    except Exception as e:
        evaluation_results["error"] = str(e)
        evaluation_results["passed"] = False
    
    return evaluation_results

def calculate_coherence_score(query: str, response: str, context: Dict) -> float:
    """Calculate semantic coherence score (simplified version)"""
    # In production, use more sophisticated semantic similarity metrics
    # For now, basic heuristics
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    overlap = len(query_words & response_words)
    score = min(1.0, overlap / max(len(query_words), 1))
    return score

def calculate_latency_score(latency_ms: float) -> float:
    """Score based on latency (lower is better)"""
    if latency_ms < 50:
        return 1.0
    elif latency_ms < 100:
        return 0.8
    elif latency_ms < 200:
        return 0.6
    elif latency_ms < 500:
        return 0.4
    else:
        return 0.2

# A2A Protocol Endpoints

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Return agent card for A2A discovery"""
    return JSONResponse(content=AGENT_CARD)

@app.post("/v1/tasks")
async def create_task(request: TaskRequest) -> TaskResponse:
    """
    Create new evaluation task (A2A protocol)
    """
    task_id = create_task_id()
    
    # Extract assessment request from messages
    assessment_config = request.config or {}
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
        "config": assessment_config,
        "messages": [m.dict() for m in request.messages],
        "results": None
    }
    
    # Start evaluation asynchronously
    asyncio.create_task(run_evaluation(task_id))
    
    return TaskResponse(
        task_id=task_id,
        status="working",
        messages=[create_response_message(f"Evaluation task {task_id} started. Processing multilingual research benchmark...")],
        artifacts=None,
        metrics=None
    )

async def run_evaluation(task_id: str):
    """Run the evaluation asynchronously"""
    task = tasks_db[task_id]
    task["status"] = "working"
    
    try:
        # Run evaluation
        results = await evaluate_agent_response(
            task["query"],
            task["agent_response"],
            task["config"]
        )
        
        task["results"] = results
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)

@app.post("/v1/tasks/{task_id}/messages")
async def send_message(task_id: str, message: Message) -> TaskResponse:
    """
    Send additional message to task (A2A protocol)
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task["messages"].append(message.dict())
    
    # If task is completed, return results
    if task["status"] == "completed":
        results = task["results"]
        
        response_text = f"""
Quantum LIMIT-GRAPH Evaluation Results:

Overall Score: {results['overall_score']:.2f}
Status: {"PASSED" if results['passed'] else "FAILED"}

Component Scores:
- Parsing Accuracy: {results['scores']['parsing_accuracy']:.2f}
- Semantic Coherence: {results['scores']['semantic_coherence']:.2f}
- Hallucination Avoidance: {results['scores']['hallucination_avoidance']:.2f}
- Latency Performance: {results['scores']['latency_score']:.2f}
- Quantum Performance: {results['scores']['quantum_performance']:.2f}

Metrics:
- Detected Language: {results.get('detected_language', 'unknown')}
- Hallucination Rate: {results['metrics']['hallucination_rate']:.4f}
- Traversal Latency: {results['metrics']['traversal_latency_ms']:.2f}ms
- Quantum Speedup: {results['metrics']['quantum_speedup']:.2f}x
"""
        
        return TaskResponse(
            task_id=task_id,
            status="completed",
            messages=[create_response_message(response_text, data=results)],
            artifacts=[{
                "type": "evaluation_results",
                "data": results
            }],
            metrics=results["metrics"]
        )
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        messages=[create_response_message(f"Task {task_id} is {task['status']}")],
        artifacts=None,
        metrics=None
    )

@app.get("/v1/tasks/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    """Get task status (A2A protocol)"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    messages = []
    artifacts = None
    metrics = None
    
    if task["status"] == "completed" and task["results"]:
        results = task["results"]
        messages = [create_response_message("Evaluation completed", data=results)]
        artifacts = [{"type": "evaluation_results", "data": results}]
        metrics = results["metrics"]
    elif task["status"] == "failed":
        messages = [create_response_message(f"Evaluation failed: {task.get('error', 'Unknown error')}")]
    else:
        messages = [create_response_message(f"Task is {task['status']}")]
    
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        messages=messages,
        artifacts=artifacts,
        metrics=metrics
    )

@app.get("/v1/tasks")
async def list_tasks(limit: int = 100) -> Dict[str, Any]:
    """List all tasks (A2A protocol)"""
    tasks_list = list(tasks_db.values())[-limit:]
    return {
        "tasks": tasks_list,
        "total": len(tasks_db),
        "limit": limit
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "Quantum LIMIT-GRAPH",
        "version": "2.3.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Main entry point
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
