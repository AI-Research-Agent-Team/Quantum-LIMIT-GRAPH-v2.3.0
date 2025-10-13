# -*- coding: utf-8 -*-
"""
Context Layer Balance Testing for Quantum LIMIT-GRAPH v2.3.0
Validates context layer density and redundancy (<12%)
"""

from typing import Dict, List, Tuple
import numpy as np
from dataclasses import dataclass
import sys
sys.path.append('..')

from src.context.ace_context_router import ACEContextRouter, ContextLayer, ContextEntry

@dataclass
class LayerBalanceMetrics:
    """Metrics for layer balance"""
    layer: str
    entry_count: int
    density: float
    redundancy: float
    balance_score: float
    passes_threshold: bool

class LayerBalanceTest:
    """
    Tests and validates context layer balance
    Ensures density and redundancy stay within acceptable thresholds
    """
    
    REDUNDANCY_THRESHOLD = 0.12  # 12% maximum redundancy
    MIN_DENSITY = 0.1  # Minimum 10% of total capacity
    MAX_DENSITY = 0.5  # Maximum 50% of total capacity
    
    def __init__(self, router: ACEContextRouter):
        """
        Initialize layer balance tester
        
        Args:
            router: ACE context router to test
        """
        self.router = router
        
    def compute_density(self, layer: ContextLayer, total_capacity: int = 1000) -> float:
        """
        Compute layer density (percentage of capacity used)
        
        Args:
            layer: Context layer
            total_capacity: Total capacity per layer
            
        Returns:
            Density score (0.0 to 1.0)
        """
        entry_count = len(self.router.context_store[layer])
        return entry_count / total_capacity
    
    def compute_redundancy(self, layer: ContextLayer, similarity_threshold: float = 0.95) -> float:
        """
        Compute redundancy within a layer
        
        Args:
            layer: Context layer
            similarity_threshold: Threshold for considering entries redundant
            
        Returns:
            Redundancy ratio (0.0 to 1.0)
        """
        entries = self.router.context_store[layer]
        
        if len(entries) < 2:
            return 0.0
        
        redundant_pairs = 0
        total_pairs = 0
        
        # Compare all pairs
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                total_pairs += 1
                
                # Compute similarity
                similarity = self.router.compute_similarity(
                    entries[i].embedding,
                    entries[j].embedding
                )
                
                if similarity >= similarity_threshold:
                    redundant_pairs += 1
        
        return redundant_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def compute_balance_score(self, density: float, redundancy: float) -> float:
        """
        Compute overall balance score
        
        Args:
            density: Layer density
            redundancy: Layer redundancy
            
        Returns:
            Balance score (0.0 to 1.0, higher is better)
        """
        # Penalize extreme densities
        density_score = 1.0 - abs(density - 0.3) / 0.3  # Optimal around 30%
        density_score = max(0.0, density_score)
        
        # Penalize high redundancy
        redundancy_score = 1.0 - (redundancy / self.REDUNDANCY_THRESHOLD)
        redundancy_score = max(0.0, redundancy_score)
        
        # Weighted combination
        return 0.6 * density_score + 0.4 * redundancy_score
    
    def test_layer(self, layer: ContextLayer) -> LayerBalanceMetrics:
        """
        Test single layer balance
        
        Args:
            layer: Context layer to test
            
        Returns:
            Layer balance metrics
        """
        entry_count = len(self.router.context_store[layer])
        density = self.compute_density(layer)
        redundancy = self.compute_redundancy(layer)
        balance_score = self.compute_balance_score(density, redundancy)
        
        # Check if passes thresholds
        passes = (
            redundancy <= self.REDUNDANCY_THRESHOLD and
            self.MIN_DENSITY <= density <= self.MAX_DENSITY
        )
        
        return LayerBalanceMetrics(
            layer=layer.value,
            entry_count=entry_count,
            density=density,
            redundancy=redundancy,
            balance_score=balance_score,
            passes_threshold=passes
        )
    
    def test_all_layers(self) -> Dict[str, LayerBalanceMetrics]:
        """
        Test all context layers
        
        Returns:
            Dictionary mapping layer names to metrics
        """
        results = {}
        
        for layer in ContextLayer:
            metrics = self.test_layer(layer)
            results[layer.value] = metrics
        
        return results
    
    def generate_report(self) -> str:
        """
        Generate comprehensive balance report
        
        Returns:
            Report string
        """
        results = self.test_all_layers()
        
        report = []
        report.append("="*60)
        report.append("CONTEXT LAYER BALANCE TEST REPORT")
        report.append("="*60)
        report.append("")
        
        all_pass = True
        
        for layer_name, metrics in results.items():
            report.append(f"Layer: {layer_name.upper()}")
            report.append(f"  Entry Count: {metrics.entry_count}")
            report.append(f"  Density: {metrics.density:.2%}")
            report.append(f"  Redundancy: {metrics.redundancy:.2%} (threshold: {self.REDUNDANCY_THRESHOLD:.2%})")
            report.append(f"  Balance Score: {metrics.balance_score:.3f}")
            report.append(f"  Status: {'✓ PASS' if metrics.passes_threshold else '✗ FAIL'}")
            report.append("")
            
            if not metrics.passes_threshold:
                all_pass = False
        
        report.append("="*60)
        report.append(f"Overall Status: {'✓ ALL TESTS PASSED' if all_pass else '✗ SOME TESTS FAILED'}")
        report.append("="*60)
        
        return "\n".join(report)
    
    def validate_balance(self) -> bool:
        """
        Validate that all layers meet balance requirements
        
        Returns:
            True if all layers pass, False otherwise
        """
        results = self.test_all_layers()
        return all(metrics.passes_threshold for metrics in results.values())


def create_test_router_with_data() -> ACEContextRouter:
    """Create test router with sample data"""
    router = ACEContextRouter()
    
    # Add sample entries to each layer
    for layer in ContextLayer:
        for i in range(20):
            # Create random embedding
            embedding = np.random.randn(768)
            embedding = embedding / np.linalg.norm(embedding)
            
            entry = ContextEntry(
                content=f"Sample content {i} for {layer.value}",
                layer=layer,
                embedding=embedding,
                language='en',
                domain='test' if layer == ContextLayer.DOMAIN else None
            )
            
            router.add_context(entry)
    
    return router


def run_layer_balance_test():
    """Run layer balance test"""
    print("Creating test router with sample data...")
    router = create_test_router_with_data()
    
    print("Running layer balance tests...\n")
    tester = LayerBalanceTest(router)
    
    report = tester.generate_report()
    print(report)
    
    return tester.validate_balance()


if __name__ == '__main__':
    success = run_layer_balance_test()
    exit(0 if success else 1)
