"""
Quantum LIMIT-GRAPH Agent Implementation
Core evaluation logic for benchmarking AI agents
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# AgentBeats imports
from earthshaker.agent import Agent
from earthshaker.models import AssessmentRequest, Message, TaskUpdate, Artifact

# Import Quantum LIMIT-GRAPH modules (mocked for now - will use actual imports)
try:
    from quantum_integration.multilingual_parser import parse_query, detect_language
    from quantum_integration.quantum_traversal import traverse_graph, get_traversal_metrics
    from quantum_integration.ace_context_router import route_context
    from quantum_integration.repair_edit_stream import apply_edits, detect_hallucinations
    QUANTUM_MODULES_AVAILABLE = True
except ImportError:
    QUANTUM_MODULES_AVAILABLE = False
    print("⚠️  Warning: Quantum integration modules not found. Using mock implementations.")


class QuantumLimitAgent(Agent):
    """
    Green Agent for Quantum LIMIT-GRAPH Benchmark
    Evaluates purple agents on multilingual research capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.supported_languages = [
            "en", "es", "fr", "de", "zh", "ja", "ko", 
            "ar", "hi", "id", "pt", "ru", "vi", "th", "tr"
        ]
    
    async def handle_assessment(self, request: AssessmentRequest) -> AsyncIterator[TaskUpdate]:
        """
        Main assessment handler
        
        Args:
            request: Assessment request containing participants and config
            
        Yields:
            TaskUpdate: Progress updates and results
        """
        yield TaskUpdate(
            status="working",
            message="🔬 Starting Quantum LIMIT-GRAPH evaluation..."
        )
        
        # Extract participants
        participants = request.participants
        config = request.config or {}
        
        # Get test queries from config or use defaults
        test_queries = config.get("test_queries", self._get_default_queries())
        
        results = []
        
        # Evaluate each participant
        for role, endpoint in participants.items():
            yield TaskUpdate(
                status="working",
                message=f"📊 Evaluating agent: {role} at {endpoint}"
            )
            
            for idx, query_data in enumerate(test_queries):
                query = query_data["query"]
                expected_lang = query_data.get("language", "en")
                
                yield TaskUpdate(
                    status="working",
                    message=f"   Test {idx+1}/{len(test_queries)}: {query[:50]}..."
                )
                
                # Get response from purple agent
                purple_response = await self._get_purple_agent_response(endpoint, query)
                
                # Evaluate the response
                eval_result = await self._evaluate_response(
                    query=query,
                    response=purple_response,
                    expected_lang=expected_lang
                )
                
                eval_result["query"] = query
                eval_result["role"] = role
                results.append(eval_result)
                
                yield TaskUpdate(
                    status="working",
                    message=f"   ✓ Score: {eval_result['overall_score']:.2f}"
                )
        
        # Calculate aggregate scores
        final_results = self._calculate_final_scores(results)
        
        # Yield final artifact with results
        yield TaskUpdate(
            status="completed",
            message="✅ Evaluation complete!",
            artifacts=[
                Artifact(
                    type="evaluation_results",
                    data=final_results
                )
            ]
        )
    
    async def _get_purple_agent_response(self, endpoint: str, query: str) -> str:
        """Get response from purple agent via A2A"""
        # This would use the A2A client to communicate with the purple agent
        # For now, return a mock response
        return f"Mock response to: {query}"
    
    async def _evaluate_response(
        self,
        query: str,
        response: str,
        expected_lang: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single query-response pair
        
        Returns:
            Dict containing evaluation scores and metrics
        """
        evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "scores": {},
            "metrics": {},
            "passed": False
        }
        
        try:
            if QUANTUM_MODULES_AVAILABLE:
                # Real evaluation using Quantum LIMIT-GRAPH modules
                detected_lang = detect_language(query)
                tokens = parse_query(query, lang=detected_lang)
                
                context = route_context(tokens)
                traversal_metrics = await asyncio.to_thread(get_traversal_metrics, context)
                
                hallucinations = detect_hallucinations(response, context)
                hallucination_rate = len(hallucinations) / max(len(response.split()), 1)
                
                evaluation["metrics"] = {
                    "detected_language": detected_lang,
                    "parsing_success": len(tokens) > 0,
                    "traversal_latency_ms": traversal_metrics.get("latency_ms", 0),
                    "quantum_speedup": traversal_metrics.get("speedup_factor", 1.0),
                    "hallucination_rate": hallucination_rate
                }
                
                # Calculate scores
                scores = {
                    "parsing_accuracy": 1.0 if len(tokens) > 0 else 0.0,
                    "semantic_coherence": self._calculate_coherence(query, response),
                    "hallucination_avoidance": max(0.0, 1.0 - hallucination_rate * 10),
                    "latency_score": self._calculate_latency_score(traversal_metrics.get("latency_ms", 100)),
                    "quantum_performance": min(1.0, traversal_metrics.get("speedup_factor", 1.0) / 2.0)
                }
            else:
                # Mock evaluation for testing
                scores = {
                    "parsing_accuracy": 0.95,
                    "semantic_coherence": 0.75,
                    "hallucination_avoidance": 0.80,
                    "latency_score": 0.85,
                    "quantum_performance": 0.70
                }
                evaluation["metrics"] = {
                    "detected_language": expected_lang,
                    "parsing_success": True,
                    "traversal_latency_ms": 85.0,
                    "quantum_speedup": 1.4,
                    "hallucination_rate": 0.02
                }
            
            evaluation["scores"] = scores
            evaluation["overall_score"] = sum(scores.values()) / len(scores)
            evaluation["passed"] = evaluation["overall_score"] >= 0.6
            
        except Exception as e:
            evaluation["error"] = str(e)
            evaluation["passed"] = False
        
        return evaluation
    
    def _calculate_coherence(self, query: str, response: str) -> float:
        """Calculate semantic coherence score"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words)
        return min(1.0, overlap / max(len(query_words), 1) * 0.5 + 0.5)
    
    def _calculate_latency_score(self, latency_ms: float) -> float:
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
    
    def _get_default_queries(self) -> List[Dict[str, str]]:
        """Default test queries for evaluation"""
        return [
            {
                "query": "What are recent developments in quantum machine learning?",
                "language": "en"
            },
            {
                "query": "¿Cuáles son los últimos avances en aprendizaje automático cuántico?",
                "language": "es"
            },
            {
                "query": "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?",
                "language": "id"
            },
            {
                "query": "量子机器学习的最新进展是什么？",
                "language": "zh"
            }
        ]
    
    def _calculate_final_scores(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregate scores across all tests"""
        if not results:
            return {"error": "No results to aggregate"}
        
        # Aggregate scores
        score_keys = list(results[0]["scores"].keys())
        aggregated_scores = {
            key: sum(r["scores"][key] for r in results) / len(results)
            for key in score_keys
        }
        
        overall_score = sum(aggregated_scores.values()) / len(aggregated_scores)
        
        return {
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results if r["passed"]),
                "overall_score": overall_score,
                "passed": overall_score >= 0.6
            },
            "aggregated_scores": aggregated_scores,
            "detailed_results": results,
            "benchmark_info": {
                "name": "Quantum LIMIT-GRAPH v2.3.0",
                "evaluation_date": datetime.utcnow().isoformat(),
                "supported_languages": self.supported_languages
            }
        }
