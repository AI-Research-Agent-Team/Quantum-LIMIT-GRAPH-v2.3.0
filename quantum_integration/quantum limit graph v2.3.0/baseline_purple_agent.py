"""
Baseline Purple Agent for Quantum LIMIT-GRAPH Benchmark
This is a simple reference implementation showing how purple agents
should interact with the Quantum LIMIT-GRAPH green agent.
"""

import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Baseline Research Agent", version="1.0.0")

# Simple agent card for the baseline purple agent
PURPLE_AGENT_CARD = {
    "agent_info": {
        "id": "baseline-research-agent",
        "name": "Baseline Research Agent",
        "version": "1.0.0",
        "description": "Simple baseline agent for multilingual research tasks",
        "vendor": "AgentBeats Tutorial",
        "license": "Apache-2.0"
    },
    "capabilities": {
        "services": [
            {
                "service_id": "research",
                "name": "Research Assistant",
                "description": "Answers research queries across multiple languages",
                "input_types": ["text"],
                "output_types": ["text"]
            }
        ],
        "supported_protocols": ["HTTP", "A2A"],
        "agent_type": "purple_agent"
    }
}

class MessagePart(BaseModel):
    type: str
    text: str = None

class Message(BaseModel):
    role: str
    parts: list[MessagePart]

class TaskRequest(BaseModel):
    messages: list[Message]
    config: Dict[str, Any] = {}

# Knowledge base (very simplified for baseline)
KNOWLEDGE_BASE = {
    "en": {
        "quantum": "Recent advances in quantum machine learning include variational quantum algorithms and quantum neural networks.",
        "ai": "Current AI research focuses on large language models, reinforcement learning, and multi-modal learning.",
        "ml": "Machine learning developments include transformer architectures, few-shot learning, and neural architecture search."
    },
    "es": {
        "quantum": "Los avances recientes en aprendizaje automático cuántico incluyen algoritmos cuánticos variacionales y redes neuronales cuánticas.",
        "ai": "La investigación actual en IA se centra en grandes modelos de lenguaje, aprendizaje por refuerzo y aprendizaje multimodal.",
        "ml": "Los desarrollos en aprendizaje automático incluyen arquitecturas transformer, aprendizaje few-shot y búsqueda de arquitectura neuronal."
    },
    "id": {
        "quantum": "Perkembangan terbaru dalam pembelajaran mesin kuantum mencakup algoritma kuantum variasional dan jaringan saraf kuantum.",
        "ai": "Penelitian AI saat ini berfokus pada model bahasa besar, pembelajaran penguatan, dan pembelajaran multi-modal.",
        "ml": "Perkembangan pembelajaran mesin mencakup arsitektur transformer, pembelajaran few-shot, dan pencarian arsitektur neural."
    },
    "zh": {
        "quantum": "量子机器学习的最新进展包括变分量子算法和量子神经网络。",
        "ai": "当前的人工智能研究重点是大型语言模型、强化学习和多模态学习。",
        "ml": "机器学习的发展包括transformer架构、少样本学习和神经架构搜索。"
    }
}

def detect_language(text: str) -> str:
    """Simple language detection based on character sets"""
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    elif any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"
    elif any('\u0900' <= c <= '\u097f' for c in text):
        return "hi"
    else:
        # Default to English
        return "en"

def find_topic(text: str) -> str:
    """Extract main topic from query"""
    text_lower = text.lower()
    if "quantum" in text_lower or "kuantum" in text_lower or "量子" in text_lower:
        return "quantum"
    elif "machine learning" in text_lower or "ml" in text_lower or "pembelajaran" in text_lower or "机器学习" in text_lower:
        return "ml"
    else:
        return "ai"

async def generate_response(query: str) -> str:
    """Generate a research response based on the query"""
    # Detect language
    lang = detect_language(query)
    
    # If language not in our knowledge base, use English
    if lang not in KNOWLEDGE_BASE:
        lang = "en"
    
    # Find topic
    topic = find_topic(query)
    
    # Get response from knowledge base
    response = KNOWLEDGE_BASE[lang].get(topic, KNOWLEDGE_BASE[lang]["ai"])
    
    # Add some context
    if lang == "en":
        full_response = f"Based on current research: {response}"
    elif lang == "es":
        full_response = f"Según la investigación actual: {response}"
    elif lang == "id":
        full_response = f"Berdasarkan penelitian terkini: {response}"
    elif lang == "zh":
        full_response = f"根据当前研究：{response}"
    else:
        full_response = response
    
    return full_response

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Return purple agent card"""
    return PURPLE_AGENT_CARD

@app.post("/v1/tasks")
async def handle_task(request: TaskRequest):
    """Handle incoming task from green agent"""
    task_id = f"purple_task_{id(request)}"
    
    # Extract query
    query = ""
    for message in request.messages:
        if message.role == "user":
            for part in message.parts:
                if part.type == "text":
                    query = part.text
                    break
    
    # Generate response
    response = await generate_response(query)
    
    return {
        "task_id": task_id,
        "status": "completed",
        "messages": [
            {
                "role": "agent",
                "parts": [
                    {
                        "type": "text",
                        "text": response
                    }
                ]
            }
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "baseline-research-agent"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
