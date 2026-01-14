"""
Quantum LIMIT-GRAPH Green Agent for AgentX-AgentBeats Competition
Main server entry point following AgentBeats green-agent-template pattern
"""

import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime

# AgentBeats imports
from earthshaker.server import Server
from earthshaker.models import AgentCard

# Import our agent implementation
from agent import QuantumLimitAgent

# Agent Card configuration
AGENT_CARD = AgentCard(
    agent_info={
        "id": "quantum-limit-graph-evaluator",
        "name": "Quantum LIMIT-GRAPH Benchmark",
        "version": "2.3.0",
        "description": "Multilingual quantum research agent benchmark for evaluating AI agents on semantic graph traversal, context routing, and hallucination detection",
        "vendor": "AI Research Agent Team",
        "license": "Apache-2.0"
    },
    capabilities={
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
        "supported_protocols": ["A2A"],
        "security_features": ["TLS"],
        "evaluation_type": "green_agent"
    },
    technical_specs={
        "runtime_environment": "Python 3.11+",
        "resource_requirements": {
            "cpu": "2 cores",
            "memory": "4GB",
            "disk": "10GB"
        }
    }
)

def create_server(host: str = "0.0.0.0", port: int = 8000, card_url: str = None) -> Server:
    """
    Create and configure the AgentBeats server
    
    Args:
        host: Host address to bind to
        port: Port to listen on
        card_url: Public URL for the agent card (optional)
    """
    # Initialize the quantum limit agent
    agent = QuantumLimitAgent()
    
    # Create server with our agent
    server = Server(
        agent=agent,
        agent_card=AGENT_CARD,
        host=host,
        port=port,
        card_url=card_url or f"http://{host}:{port}"
    )
    
    return server

def main():
    """Main entry point"""
    # Get configuration from environment or command line
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    card_url = os.getenv("CARD_URL", None)
    
    # Create and start server
    server = create_server(host=host, port=port, card_url=card_url)
    
    print(f"🚀 Starting Quantum LIMIT-GRAPH Green Agent...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Agent Card: {card_url or f'http://{host}:{port}/.well-known/agent-card.json'}")
    
    # Run the server
    server.run()

if __name__ == "__main__":
    main()
