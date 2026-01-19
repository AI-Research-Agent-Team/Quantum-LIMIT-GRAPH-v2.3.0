"""
Quantum LIMIT-GRAPH Green Agent Server
A2A-compliant evaluation framework using quantum modules as gold standard
"""

import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime

try:
    from earthshaker.server import Server
    from earthshaker.agent import Agent
    from earthshaker.models import AgentCard, AssessmentRequest
    EARTHSHAKER_AVAILABLE = True
except ImportError:
    print("⚠️ earthshaker not available, using standalone mode")
    EARTHSHAKER_AVAILABLE = False

from orchestrator import AssessmentOrchestrator
from config import Config

# Agent Card
AGENT_CARD = {
    "agent_info": {
        "id": "quantum-limit-graph-evaluator",
        "name": "Quantum LIMIT-GRAPH Evaluator",
        "version": "2.3.0",
        "description": "Multilingual quantum NLP evaluation framework. Tests agents on language detection, quantum graph traversal, hallucination detection, and context routing using quantum-enhanced algorithms as gold standard.",
        "vendor": "AI Research Agent Team",
        "license": "Apache-2.0",
        "homepage": "https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0"
    },
    "capabilities": {
        "agent_type": "evaluator",
        "evaluation_domains": [
            "multilingual_nlp",
            "quantum_algorithms",
            "hallucination_detection",
            "context_routing"
        ],
        "services": [
            {
                "service_id": "multilingual_evaluation",
                "name": "Multilingual NLP Evaluation",
                "description": "Tests language detection and parsing across 15+ languages",
                "metrics": [
                    "language_detection_accuracy",
                    "tokenization_quality",
                    "cross_lingual_consistency"
                ]
            },
            {
                "service_id": "quantum_benchmark",
                "name": "Quantum Graph Traversal Benchmark",
                "description": "Benchmarks graph traversal against QAOA baseline",
                "metrics": [
                    "speedup_factor",
                    "traversal_efficiency",
                    "semantic_coherence"
                ]
            },
            {
                "service_id": "hallucination_detection",
                "name": "Hallucination Detection Evaluation",
                "description": "Measures factual accuracy and hallucination rates",
                "metrics": [
                    "hallucination_rate",
                    "factual_accuracy",
                    "edit_stream_quality"
                ]
            },
            {
                "service_id": "context_routing",
                "name": "Context Routing Evaluation",
                "description": "Evaluates hierarchical context routing optimization",
                "metrics": [
                    "routing_efficiency",
                    "layer_utilization",
                    "similarity_threshold_accuracy"
                ]
            }
        ],
        "supported_languages": [
            "en", "es", "fr", "de", "zh", "ja", "ko", 
            "ar", "hi", "id", "pt", "ru", "vi", "th", "tr"
        ],
        "test_suites": [
            "multilingual",
            "quantum",
            "hallucination",
            "context_routing"
        ]
    },
    "technical_specs": {
        "runtime_environment": "Python 3.11+",
        "quantum_backend": "Qiskit",
        "nlp_models": "mBART-50",
        "resource_requirements": {
            "cpu": "4 cores",
            "memory": "8GB",
            "disk": "20GB"
        }
    }
}


class QuantumLimitGreenAgent(Agent if EARTHSHAKER_AVAILABLE else object):
    """
    Green Agent for Quantum LIMIT-GRAPH Evaluation
    
    Uses quantum-enhanced NLP modules as gold standard for evaluating
    other agents on multilingual capabilities, graph traversal, 
    hallucination detection, and context routing.
    """
    
    def __init__(self):
        if EARTHSHAKER_AVAILABLE:
            super().__init__()
        
        # Load configuration
        self.config = Config()
        
        # Initialize orchestrator
        self.orchestrator = AssessmentOrchestrator(self.config)
        
        print("✅ Quantum LIMIT-GRAPH Green Agent initialized")
        print(f"   Test Suites: {len(self.config.test_suites)}")
        print(f"   Languages: {len(AGENT_CARD['capabilities']['supported_languages'])}")
    
    async def handle_assessment(self, request: AssessmentRequest) -> AsyncIterator[Dict]:
        """
        Main assessment handler for A2A protocol
        
        Flow:
        1. Receive assessment request with purple agent endpoints
        2. Load configured test suites
        3. For each purple agent:
           - Run multilingual tests (using multilingual_parser)
           - Run quantum benchmarks (using quantum_traversal)
           - Run hallucination tests (using repair_edit_stream)
           - Run context routing tests (using ace_context_router)
        4. Aggregate scores
        5. Return comprehensive results
        
        Args:
            request: AssessmentRequest containing participants and config
            
        Yields:
            Progress updates and final results
        """
        yield {
            "status": "started",
            "message": "🔬 Starting Quantum LIMIT-GRAPH evaluation",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Extract participants
        participants = request.participants
        config = request.config or {}
        
        # Override config with request config
        assessment_config = {**self.config.to_dict(), **config}
        
        yield {
            "status": "working",
            "message": f"📊 Evaluating {len(participants)} agent(s)",
            "participants": list(participants.keys())
        }
        
        # Run assessment
        try:
            results = await self.orchestrator.run_assessment(
                participants=participants,
                config=assessment_config
            )
            
            # Stream progress updates
            async for update in self.orchestrator.get_progress():
                yield update
            
            # Final results
            yield {
                "status": "completed",
                "message": "✅ Evaluation complete",
                "results": results,
                "artifacts": [
                    {
                        "type": "evaluation_results",
                        "name": "quantum_limit_graph_results.json",
                        "data": results
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            yield {
                "status": "failed",
                "message": f"❌ Evaluation failed: {str(e)}",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


def create_server(host: str = "0.0.0.0", port: int = 8000) -> Server:
    """
    Create A2A server with Quantum LIMIT-GRAPH green agent
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        Configured Server instance
    """
    agent = QuantumLimitGreenAgent()
    
    if EARTHSHAKER_AVAILABLE:
        server = Server(
            agent=agent,
            agent_card=AGENT_CARD,
            host=host,
            port=port
        )
    else:
        # Fallback standalone server
        from fastapi import FastAPI
        import uvicorn
        
        app = FastAPI(title="Quantum LIMIT-GRAPH Evaluator")
        
        @app.get("/.well-known/agent-card.json")
        async def get_agent_card():
            return AGENT_CARD
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "agent": "quantum-limit-graph-evaluator"}
        
        server = type('Server', (), {
            'run': lambda: uvicorn.run(app, host=host, port=port)
        })()
    
    return server


def main():
    """Main entry point"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    
    print("=" * 60)
    print("🚀 Quantum LIMIT-GRAPH Green Agent")
    print("=" * 60)
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Version: {AGENT_CARD['agent_info']['version']}")
    print("=" * 60)
    print()
    print("🧪 Evaluation Capabilities:")
    for service in AGENT_CARD['capabilities']['services']:
        print(f"   • {service['name']}")
    print()
    print("🌍 Supported Languages:")
    langs = AGENT_CARD['capabilities']['supported_languages']
    print(f"   {', '.join(langs[:8])}")
    print(f"   {', '.join(langs[8:])}")
    print("=" * 60)
    
    server = create_server(host, port)
    server.run()


if __name__ == "__main__":
    main()
