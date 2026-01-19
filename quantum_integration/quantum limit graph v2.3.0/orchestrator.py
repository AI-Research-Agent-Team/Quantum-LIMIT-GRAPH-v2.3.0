"""
Assessment Orchestrator
Coordinates evaluation of purple agents using quantum modules as gold standard
"""

import asyncio
from typing import Dict, List, Any, AsyncIterator
from datetime import datetime
from collections import defaultdict

from client.a2a_client import A2AClient
from test_suites.multilingual_suite import MultilingualTestSuite
from test_suites.quantum_suite import QuantumSpeedTestSuite
from test_suites.hallucination_suite import HallucinationTestSuite
from test_suites.context_routing_suite import ContextRoutingTestSuite
from evaluators.aggregator import ScoreAggregator


class AssessmentOrchestrator:
    """
    Orchestrates comprehensive agent evaluation
    
    Uses Quantum LIMIT-GRAPH modules as gold standard:
    - multilingual_parser → Language detection baseline
    - quantum_traversal → Speed/efficiency baseline  
    - repair_edit_stream → Hallucination detection oracle
    - ace_context_router → Context routing oracle
    """
    
    def __init__(self, config):
        self.config = config
        
        # Initialize test suites (using YOUR modules)
        self.test_suites = {
            "multilingual": MultilingualTestSuite(),
            "quantum": QuantumSpeedTestSuite(),
            "hallucination": HallucinationTestSuite(),
            "context_routing": ContextRoutingTestSuite()
        }
        
        # Initialize A2A client for purple agent communication
        self.a2a_client = A2AClient()
        
        # Score aggregator
        self.aggregator = ScoreAggregator()
        
        # Progress tracking
        self.progress_queue = asyncio.Queue()
    
    async def run_assessment(
        self, 
        participants: Dict[str, str],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run complete assessment
        
        Args:
            participants: Dict of {role: endpoint_url}
            config: Assessment configuration
            
        Returns:
            Comprehensive evaluation results
        """
        start_time = datetime.utcnow()
        results = {
            "assessment_id": f"assess_{int(start_time.timestamp())}",
            "timestamp": start_time.isoformat(),
            "participants": {},
            "summary": {}
        }
        
        # Get test suites to run
        suites_to_run = config.get(
            "test_suites", 
            list(self.test_suites.keys())
        )
        
        await self._emit_progress({
            "stage": "initialization",
            "message": f"Running {len(suites_to_run)} test suites",
            "suites": suites_to_run
        })
        
        # Evaluate each participant
        for role, endpoint in participants.items():
            await self._emit_progress({
                "stage": "evaluation",
                "message": f"Evaluating {role}",
                "endpoint": endpoint
            })
            
            participant_results = await self._evaluate_participant(
                role=role,
                endpoint=endpoint,
                suites=suites_to_run,
                config=config
            )
            
            results["participants"][role] = participant_results
        
        # Aggregate scores
        results["summary"] = self.aggregator.aggregate_results(
            results["participants"]
        )
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        results["duration_seconds"] = duration
        
        await self._emit_progress({
            "stage": "completed",
            "message": "Assessment complete",
            "duration": duration
        })
        
        return results
    
    async def _evaluate_participant(
        self,
        role: str,
        endpoint: str,
        suites: List[str],
        config: Dict
    ) -> Dict[str, Any]:
        """
        Evaluate single participant across all test suites
        
        Args:
            role: Participant role name
            endpoint: Purple agent A2A endpoint
            suites: Test suites to run
            config: Configuration
            
        Returns:
            Participant evaluation results
        """
        results = {
            "role": role,
            "endpoint": endpoint,
            "test_results": {},
            "metrics": {},
            "scores": {}
        }
        
        # Create purple agent proxy
        purple_agent = self.a2a_client.create_proxy(endpoint)
        
        # Run each test suite
        for suite_name in suites:
            if suite_name not in self.test_suites:
                continue
            
            suite = self.test_suites[suite_name]
            
            await self._emit_progress({
                "stage": "testing",
                "participant": role,
                "suite": suite_name,
                "message": f"Running {suite_name} tests"
            })
            
            try:
                # Run test suite
                suite_results = await suite.evaluate(
                    purple_agent=purple_agent,
                    config=config
                )
                
                results["test_results"][suite_name] = suite_results
                results["scores"][suite_name] = suite_results.get("score", 0.0)
                
                # Extract metrics
                if "metrics" in suite_results:
                    for metric, value in suite_results["metrics"].items():
                        results["metrics"][f"{suite_name}_{metric}"] = value
                
                await self._emit_progress({
                    "stage": "testing",
                    "participant": role,
                    "suite": suite_name,
                    "score": suite_results.get("score", 0.0),
                    "message": f"✅ {suite_name} complete"
                })
                
            except Exception as e:
                results["test_results"][suite_name] = {
                    "error": str(e),
                    "status": "failed"
                }
                results["scores"][suite_name] = 0.0
                
                await self._emit_progress({
                    "stage": "testing",
                    "participant": role,
                    "suite": suite_name,
                    "error": str(e),
                    "message": f"❌ {suite_name} failed"
                })
        
        # Calculate overall score
        if results["scores"]:
            results["overall_score"] = sum(results["scores"].values()) / len(results["scores"])
        else:
            results["overall_score"] = 0.0
        
        return results
    
    async def _emit_progress(self, update: Dict):
        """Emit progress update"""
        await self.progress_queue.put({
            **update,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_progress(self) -> AsyncIterator[Dict]:
        """Get progress updates"""
        while True:
            try:
                update = await asyncio.wait_for(
                    self.progress_queue.get(), 
                    timeout=0.1
                )
                yield update
            except asyncio.TimeoutError:
                break
