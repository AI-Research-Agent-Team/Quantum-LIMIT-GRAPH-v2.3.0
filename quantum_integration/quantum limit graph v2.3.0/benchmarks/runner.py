"""
Quantum LIMIT-GRAPH Benchmark Runner
Scalable benchmark execution with parallel processing and AgentBeats integration
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from benchmarks.suites.multilingual_suite import MultilingualSuite
from benchmarks.suites.quantum_suite import QuantumSuite
from benchmarks.suites.hallucination_suite import HallucinationSuite
from benchmarks.suites.scalability_suite import ScalabilitySuite
from benchmarks.reporters.json_reporter import JSONReporter
from benchmarks.reporters.html_reporter import HTMLReporter
from benchmarks.reporters.agentbeats_reporter import AgentBeatsReporter
from monitoring.logger import logger


class BenchmarkRunner:
    """
    Main benchmark runner with parallel execution support
    """
    
    def __init__(
        self,
        config_path: str = "benchmarks/config/benchmarks.yaml",
        max_workers: Optional[int] = None
    ):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.max_workers = max_workers or mp.cpu_count()
        
        # Initialize test suites
        self.suites = {
            "multilingual": MultilingualSuite(),
            "quantum": QuantumSuite(),
            "hallucination": HallucinationSuite(),
            "scalability": ScalabilitySuite()
        }
        
        # Initialize reporters
        self.reporters = {
            "json": JSONReporter(),
            "html": HTMLReporter(),
            "agentbeats": AgentBeatsReporter()
        }
        
        self.results = []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load benchmark configuration"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        """Default benchmark configuration"""
        return {
            "suites": ["multilingual", "quantum", "hallucination"],
            "parallel": True,
            "timeout": 300,
            "retry_failed": True,
            "max_retries": 3,
            "output_formats": ["json", "html", "agentbeats"]
        }
    
    async def run_benchmark_suite(
        self,
        suite_name: str,
        agent_endpoint: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Run a single benchmark suite
        
        Args:
            suite_name: Name of the suite to run
            agent_endpoint: URL of the agent to test
            agent_id: Unique agent identifier
            
        Returns:
            Dict containing suite results
        """
        if suite_name not in self.suites:
            raise ValueError(f"Unknown suite: {suite_name}")
        
        suite = self.suites[suite_name]
        
        logger.info(
            f"Starting {suite_name} suite for agent {agent_id}",
            extra={"suite": suite_name, "agent": agent_id}
        )
        
        start_time = datetime.utcnow()
        
        try:
            # Run the suite
            results = await suite.run(
                agent_endpoint=agent_endpoint,
                agent_id=agent_id,
                timeout=self.config.get("timeout", 300)
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            suite_result = {
                "suite": suite_name,
                "agent_id": agent_id,
                "status": "completed",
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "results": results,
                "summary": self._calculate_summary(results)
            }
            
            logger.info(
                f"Completed {suite_name} suite",
                extra={
                    "suite": suite_name,
                    "duration": duration,
                    "score": suite_result["summary"].get("overall_score")
                }
            )
            
            return suite_result
            
        except Exception as e:
            logger.error(
                f"Error in {suite_name} suite: {e}",
                extra={"suite": suite_name, "error": str(e)}
            )
            
            return {
                "suite": suite_name,
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e),
                "timestamp": start_time.isoformat()
            }
    
    def _calculate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from suite results"""
        scores = []
        
        # Extract scores from results
        if isinstance(results, dict):
            if "scores" in results:
                scores = list(results["scores"].values())
            elif "test_results" in results:
                scores = [
                    test.get("score", 0.0) 
                    for test in results["test_results"]
                    if "score" in test
                ]
        
        if not scores:
            return {"overall_score": 0.0}
        
        return {
            "overall_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "tests_passed": sum(1 for s in scores if s >= 0.6),
            "tests_total": len(scores),
            "pass_rate": sum(1 for s in scores if s >= 0.6) / len(scores)
        }
    
    async def run_all_suites(
        self,
        agent_endpoint: str,
        agent_id: str,
        suites: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run all configured benchmark suites
        
        Args:
            agent_endpoint: URL of the agent to test
            agent_id: Unique agent identifier
            suites: Optional list of suite names (uses config if None)
            
        Returns:
            Dict containing all results
        """
        suites_to_run = suites or self.config.get("suites", list(self.suites.keys()))
        
        logger.info(
            f"Running {len(suites_to_run)} benchmark suites for {agent_id}",
            extra={"suites": suites_to_run, "agent": agent_id}
        )
        
        start_time = datetime.utcnow()
        
        if self.config.get("parallel", True):
            # Run suites in parallel
            tasks = [
                self.run_benchmark_suite(suite, agent_endpoint, agent_id)
                for suite in suites_to_run
            ]
            suite_results = await asyncio.gather(*tasks)
        else:
            # Run suites sequentially
            suite_results = []
            for suite in suites_to_run:
                result = await self.run_benchmark_suite(suite, agent_endpoint, agent_id)
                suite_results.append(result)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Aggregate results
        aggregated = {
            "agent_id": agent_id,
            "agent_endpoint": agent_endpoint,
            "benchmark_version": "2.3.0",
            "timestamp": start_time.isoformat(),
            "duration_seconds": duration,
            "suites_run": len(suite_results),
            "suite_results": suite_results,
            "overall_summary": self._aggregate_summaries(suite_results)
        }
        
        self.results.append(aggregated)
        
        logger.info(
            f"All benchmarks completed for {agent_id}",
            extra={
                "duration": duration,
                "overall_score": aggregated["overall_summary"].get("overall_score")
            }
        )
        
        return aggregated
    
    def _aggregate_summaries(self, suite_results: List[Dict]) -> Dict[str, Any]:
        """Aggregate summaries from multiple suites"""
        all_scores = []
        
        for suite in suite_results:
            if suite.get("status") == "completed":
                summary = suite.get("summary", {})
                if "overall_score" in summary:
                    all_scores.append(summary["overall_score"])
        
        if not all_scores:
            return {"overall_score": 0.0}
        
        return {
            "overall_score": sum(all_scores) / len(all_scores),
            "suites_passed": sum(1 for s in all_scores if s >= 0.6),
            "suites_total": len(suite_results),
            "min_suite_score": min(all_scores),
            "max_suite_score": max(all_scores)
        }
    
    async def run_batch(
        self,
        agents: List[Dict[str, str]],
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run benchmarks for multiple agents
        
        Args:
            agents: List of dicts with 'endpoint' and 'id' keys
            parallel: Whether to run agents in parallel
            
        Returns:
            List of results for all agents
        """
        logger.info(f"Running batch benchmark for {len(agents)} agents")
        
        if parallel:
            tasks = [
                self.run_all_suites(agent["endpoint"], agent["id"])
                for agent in agents
            ]
            results = await asyncio.gather(*tasks)
        else:
            results = []
            for agent in agents:
                result = await self.run_all_suites(agent["endpoint"], agent["id"])
                results.append(result)
        
        return results
    
    async def save_results(
        self,
        output_dir: str = "benchmark_results",
        formats: Optional[List[str]] = None
    ):
        """
        Save benchmark results in specified formats
        
        Args:
            output_dir: Directory to save results
            formats: Output formats (uses config if None)
        """
        if not self.results:
            logger.warning("No results to save")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        formats_to_use = formats or self.config.get("output_formats", ["json"])
        
        for format_name in formats_to_use:
            if format_name not in self.reporters:
                logger.warning(f"Unknown format: {format_name}")
                continue
            
            reporter = self.reporters[format_name]
            
            try:
                filename = reporter.save(
                    results=self.results,
                    output_dir=str(output_path)
                )
                logger.info(f"Saved {format_name} report: {filename}")
            except Exception as e:
                logger.error(f"Error saving {format_name} report: {e}")
    
    async def submit_to_agentbeats(
        self,
        leaderboard_webhook: str,
        results: Optional[Dict] = None
    ):
        """
        Submit results to AgentBeats leaderboard
        
        Args:
            leaderboard_webhook: AgentBeats webhook URL
            results: Results to submit (uses latest if None)
        """
        if results is None:
            if not self.results:
                logger.error("No results to submit")
                return
            results = self.results[-1]
        
        reporter = self.reporters["agentbeats"]
        
        try:
            response = await reporter.submit(
                results=results,
                webhook_url=leaderboard_webhook
            )
            logger.info(f"Submitted to AgentBeats: {response}")
        except Exception as e:
            logger.error(f"Error submitting to AgentBeats: {e}")


async def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quantum LIMIT-GRAPH Benchmark Runner"
    )
    parser.add_argument(
        "--agent-endpoint",
        required=True,
        help="Agent A2A endpoint URL"
    )
    parser.add_argument(
        "--agent-id",
        required=True,
        help="Unique agent identifier"
    )
    parser.add_argument(
        "--suites",
        nargs="+",
        help="Specific suites to run (default: all)"
    )
    parser.add_argument(
        "--config",
        default="benchmarks/config/benchmarks.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--submit",
        help="AgentBeats webhook URL for submission"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run suites in parallel"
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = BenchmarkRunner(config_path=args.config)
    
    # Run benchmarks
    results = await runner.run_all_suites(
        agent_endpoint=args.agent_endpoint,
        agent_id=args.agent_id,
        suites=args.suites
    )
    
    # Save results
    await runner.save_results(output_dir=args.output_dir)
    
    # Submit to AgentBeats if requested
    if args.submit:
        await runner.submit_to_agentbeats(
            leaderboard_webhook=args.submit,
            results=results
        )
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Agent ID: {results['agent_id']}")
    print(f"Overall Score: {results['overall_summary']['overall_score']:.3f}")
    print(f"Suites Passed: {results['overall_summary']['suites_passed']}/{results['overall_summary']['suites_total']}")
    print(f"Duration: {results['duration_seconds']:.2f}s")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
