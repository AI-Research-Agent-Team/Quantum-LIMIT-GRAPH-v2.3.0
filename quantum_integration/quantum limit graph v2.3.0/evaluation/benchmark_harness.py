# -*- coding: utf-8 -*-
"""
Benchmark Harness for Quantum LIMIT-GRAPH v2.3.0
Runs multilingual edit reliability tests
Compares quantum vs. classical traversal latency
"""

from typing import Dict, List, Tuple
import time
import json
from dataclasses import dataclass, asdict
import numpy as np
import sys
sys.path.append('..')

from src.agent.multilingual_parser import MultilingualParser
from src.graph.quantum_traversal import QuantumGraphTraversal
from src.agent.repair_edit_stream import REPAIREditStream
import networkx as nx

@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    test_name: str
    language: str
    method: str
    latency_ms: float
    accuracy: float
    edit_count: int
    hallucination_rate: float
    success: bool

class BenchmarkHarness:
    """
    Comprehensive benchmark harness for multilingual quantum LIMIT-GRAPH
    """
    
    def __init__(self):
        """Initialize benchmark harness"""
        self.parser = MultilingualParser()
        self.edit_stream = REPAIREditStream()
        self.results: List[BenchmarkResult] = []
        
    def create_test_graph(self, size: int = 20) -> nx.Graph:
        """
        Create test graph for benchmarking
        
        Args:
            size: Number of nodes
            
        Returns:
            Test graph
        """
        G = nx.Graph()
        
        # Create connected graph
        for i in range(size):
            for j in range(i + 1, min(i + 4, size)):
                weight = np.random.uniform(0.6, 0.95)
                edge_type = np.random.choice(['semantic', 'citation'])
                G.add_edge(f'node_{i}', f'node_{j}', weight=weight, type=edge_type)
        
        return G
    
    def benchmark_multilingual_parsing(self, test_queries: Dict[str, str]) -> List[BenchmarkResult]:
        """
        Benchmark multilingual parsing across languages
        
        Args:
            test_queries: Dictionary mapping language codes to test queries
            
        Returns:
            List of benchmark results
        """
        results = []
        
        for lang, query in test_queries.items():
            start_time = time.time()
            
            try:
                parsed = self.parser.parse_query(query, lang)
                latency = (time.time() - start_time) * 1000
                
                # Verify language detection
                detected_lang = parsed['language']
                accuracy = 1.0 if detected_lang == lang else 0.0
                
                result = BenchmarkResult(
                    test_name='multilingual_parsing',
                    language=lang,
                    method='mbart50',
                    latency_ms=latency,
                    accuracy=accuracy,
                    edit_count=0,
                    hallucination_rate=0.0,
                    success=True
                )
                
            except Exception as e:
                result = BenchmarkResult(
                    test_name='multilingual_parsing',
                    language=lang,
                    method='mbart50',
                    latency_ms=0.0,
                    accuracy=0.0,
                    edit_count=0,
                    hallucination_rate=0.0,
                    success=False
                )
            
            results.append(result)
        
        return results
    
    def benchmark_traversal_methods(self, graph: nx.Graph, num_trials: int = 10) -> List[BenchmarkResult]:
        """
        Compare quantum vs classical traversal
        
        Args:
            graph: Test graph
            num_trials: Number of trials per method
            
        Returns:
            List of benchmark results
        """
        results = []
        nodes = list(graph.nodes())
        
        for method_name, use_quantum in [('quantum_qaoa', True), ('classical_dijkstra', False)]:
            traversal = QuantumGraphTraversal(graph, use_quantum=use_quantum)
            
            latencies = []
            accuracies = []
            
            for _ in range(num_trials):
                # Random start and target
                start = np.random.choice(nodes)
                target = np.random.choice([n for n in nodes if n != start])
                
                start_time = time.time()
                result = traversal.traverse(start, target)
                latency = (time.time() - start_time) * 1000
                
                latencies.append(latency)
                
                # Accuracy based on coherence
                accuracies.append(result['coherence'])
            
            benchmark_result = BenchmarkResult(
                test_name='traversal_comparison',
                language='en',
                method=method_name,
                latency_ms=np.mean(latencies),
                accuracy=np.mean(accuracies),
                edit_count=0,
                hallucination_rate=0.0,
                success=True
            )
            
            results.append(benchmark_result)
        
        return results
    
    def benchmark_edit_reliability(self, test_cases: List[Dict]) -> List[BenchmarkResult]:
        """
        Benchmark REPAIR edit reliability
        
        Args:
            test_cases: List of test cases with text and expected edits
            
        Returns:
            List of benchmark results
        """
        results = []
        
        for test_case in test_cases:
            text = test_case['text']
            lang = test_case['language']
            context = test_case.get('context', {})
            
            start_time = time.time()
            edit_result = self.edit_stream.apply_edits(text, context)
            latency = (time.time() - start_time) * 1000
            
            # Calculate metrics
            edits_applied = len(edit_result['edits_applied'])
            hallucination_detected = edit_result['hallucination_detected'] is not None
            hallucination_rate = 1.0 if hallucination_detected else 0.0
            
            result = BenchmarkResult(
                test_name='edit_reliability',
                language=lang,
                method='repair_stream',
                latency_ms=latency,
                accuracy=edit_result['reliability_score'],
                edit_count=edits_applied,
                hallucination_rate=hallucination_rate,
                success=True
            )
            
            results.append(result)
        
        return results
    
    def run_full_benchmark(self) -> Dict:
        """
        Run complete benchmark suite
        
        Returns:
            Comprehensive benchmark results
        """
        print("Starting Quantum LIMIT-GRAPH v2.3.0 Benchmark...")
        
        # Test queries in multiple languages
        test_queries = {
            'en': 'What are the latest developments in quantum machine learning?',
            'es': '¿Cuáles son los últimos avances en aprendizaje automático cuántico?',
            'zh': '量子机器学习的最新发展是什么？',
            'ar': 'ما هي أحدث التطورات في التعلم الآلي الكمي؟',
            'hi': 'क्वांटम मशीन लर्निंग में नवीनतम विकास क्या हैं?',
            'id': 'Apa perkembangan terbaru dalam pembelajaran mesin kuantum?'
        }
        
        # 1. Multilingual parsing benchmark
        print("\n1. Benchmarking multilingual parsing...")
        parsing_results = self.benchmark_multilingual_parsing(test_queries)
        self.results.extend(parsing_results)
        
        # 2. Traversal comparison benchmark
        print("2. Benchmarking quantum vs classical traversal...")
        test_graph = self.create_test_graph(size=15)
        traversal_results = self.benchmark_traversal_methods(test_graph, num_trials=5)
        self.results.extend(traversal_results)
        
        # 3. Edit reliability benchmark
        print("3. Benchmarking REPAIR edit reliability...")
        edit_test_cases = [
            {
                'text': 'Research shows quantum computers are faster.',
                'language': 'en',
                'context': {'entities': ['quantum', 'computers'], 'source': 'test'}
            },
            {
                'text': 'Los estudios demuestran que las computadoras cuánticas son más rápidas.',
                'language': 'es',
                'context': {'entities': ['computadoras', 'cuánticas'], 'source': 'test'}
            }
        ]
        edit_results = self.benchmark_edit_reliability(edit_test_cases)
        self.results.extend(edit_results)
        
        # Aggregate results
        return self.aggregate_results()
    
    def aggregate_results(self) -> Dict:
        """Aggregate benchmark results"""
        aggregated = {
            'total_tests': len(self.results),
            'success_rate': sum(r.success for r in self.results) / len(self.results),
            'by_test': {},
            'by_language': {},
            'by_method': {},
            'detailed_results': [asdict(r) for r in self.results]
        }
        
        # Aggregate by test name
        for result in self.results:
            test_name = result.test_name
            if test_name not in aggregated['by_test']:
                aggregated['by_test'][test_name] = {
                    'count': 0,
                    'avg_latency_ms': 0.0,
                    'avg_accuracy': 0.0,
                    'success_rate': 0.0
                }
            
            stats = aggregated['by_test'][test_name]
            stats['count'] += 1
            stats['avg_latency_ms'] += result.latency_ms
            stats['avg_accuracy'] += result.accuracy
            stats['success_rate'] += (1.0 if result.success else 0.0)
        
        # Calculate averages
        for test_name, stats in aggregated['by_test'].items():
            count = stats['count']
            stats['avg_latency_ms'] /= count
            stats['avg_accuracy'] /= count
            stats['success_rate'] /= count
        
        return aggregated
    
    def save_results(self, filepath: str = 'benchmark_results.json'):
        """Save results to file"""
        results = self.aggregate_results()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {filepath}")


def run_benchmark():
    """Run benchmark harness"""
    harness = BenchmarkHarness()
    results = harness.run_full_benchmark()
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Success Rate: {results['success_rate']:.2%}")
    print("\nBy Test Type:")
    for test_name, stats in results['by_test'].items():
        print(f"\n  {test_name}:")
        print(f"    Avg Latency: {stats['avg_latency_ms']:.2f} ms")
        print(f"    Avg Accuracy: {stats['avg_accuracy']:.2%}")
        print(f"    Success Rate: {stats['success_rate']:.2%}")
    
    harness.save_results()
    return results


if __name__ == '__main__':
    run_benchmark()
