import concurrent.futures
import time
import json
from src.quantum_graph import QuantumGraph # Assuming this is your core class

class BenchmarkRunner:
    def __init__(self, scenarios):
        self.scenarios = scenarios
        self.results = []

    def run_single_scenario(self, scenario):
        """Runs one specific graph limit test case."""
        start_time = time.perf_counter()
        
        # Initialize your research model
        qg = QuantumGraph(nodes=scenario['nodes'], limit_type=scenario['type'])
        result = qg.optimize() # Run the heavy computation
        
        duration = time.perf_counter() - start_time
        return {
            "id": scenario['id'],
            "accuracy": result['accuracy'],
            "energy_gap": result['energy_gap'],
            "duration": duration,
            "status": "success" if result['converged'] else "failed"
        }

    def run_parallel(self, workers=4):
        """Scales execution across CPU cores."""
        print(f"🚀 Starting Benchmark on {len(self.scenarios)} scenarios with {workers} workers...")
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(self.run_single_scenario, s) for s in self.scenarios]
            
            for future in concurrent.futures.as_completed(futures):
                self.results.append(future.result())
        
        return self.generate_report()

    def generate_report(self):
        # Calculate aggregate metrics for the Leaderboard
        avg_acc = sum(r['accuracy'] for r in self.results) / len(self.results)
        return {
            "total_score": avg_acc,
            "latency_ms": sum(r['duration'] for r in self.results) * 1000,
            "details": self.results
        }
