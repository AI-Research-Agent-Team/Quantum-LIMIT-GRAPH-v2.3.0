# -*- coding: utf-8 -*-
"""
Quantum Graph Traversal for LIMIT-GRAPH v2.3.0
Implements QAOA-based graph traversal with citation walks and semantic coherence
Supports fallback to classical traversal
"""

from typing import List, Dict, Tuple, Optional, Set
import numpy as np
import networkx as nx
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
import time

class QuantumGraphTraversal:
    """
    QAOA-based graph traversal with citation walks and semantic coherence scoring
    """
    
    def __init__(self, graph: nx.Graph, use_quantum: bool = True):
        """
        Initialize quantum traversal engine
        
        Args:
            graph: NetworkX graph representing semantic knowledge
            use_quantum: Whether to use quantum traversal (fallback to classical if False)
        """
        self.graph = graph
        self.use_quantum = use_quantum
        self.sampler = Sampler()
        self.optimizer = COBYLA(maxiter=100)
        
    def compute_semantic_coherence(self, path: List[str]) -> float:
        """
        Compute semantic coherence score for a traversal path
        
        Args:
            path: List of node IDs in traversal order
            
        Returns:
            Coherence score (0.0 to 1.0)
        """
        if len(path) < 2:
            return 1.0
        
        coherence_scores = []
        for i in range(len(path) - 1):
            node1, node2 = path[i], path[i + 1]
            
            # Check if edge exists
            if self.graph.has_edge(node1, node2):
                edge_data = self.graph[node1][node2]
                weight = edge_data.get('weight', 0.5)
                coherence_scores.append(weight)
            else:
                # Penalize non-adjacent nodes
                coherence_scores.append(0.1)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    def citation_walk(self, start_node: str, max_depth: int = 3) -> List[str]:
        """
        Perform citation-based walk through graph
        
        Args:
            start_node: Starting node ID
            max_depth: Maximum depth of citation walk
            
        Returns:
            List of cited nodes
        """
        visited = set()
        citation_path = []
        queue = [(start_node, 0)]
        
        while queue:
            node, depth = queue.pop(0)
            
            if node in visited or depth > max_depth:
                continue
            
            visited.add(node)
            citation_path.append(node)
            
            # Get neighbors with citation edges
            for neighbor in self.graph.neighbors(node):
                edge_data = self.graph[node][neighbor]
                if edge_data.get('type') == 'citation' and neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return citation_path
    
    def qaoa_traversal(self, start_node: str, target_node: str, num_layers: int = 2) -> Tuple[List[str], float]:
        """
        QAOA-based optimal path finding
        
        Args:
            start_node: Starting node
            target_node: Target node
            num_layers: Number of QAOA layers
            
        Returns:
            Tuple of (optimal path, cost)
        """
        try:
            # Get shortest path candidates
            if not nx.has_path(self.graph, start_node, target_node):
                return [start_node], 0.0
            
            all_paths = list(nx.all_simple_paths(
                self.graph, start_node, target_node, cutoff=5
            ))
            
            if not all_paths:
                return [start_node], 0.0
            
            # Limit to top 10 paths for quantum optimization
            all_paths = all_paths[:10]
            
            # Create quadratic program
            qp = QuadraticProgram()
            for i in range(len(all_paths)):
                qp.binary_var(f'x{i}')
            
            # Objective: minimize path length weighted by coherence
            linear = {}
            for i, path in enumerate(all_paths):
                coherence = self.compute_semantic_coherence(path)
                cost = len(path) * (1.0 - coherence)
                linear[f'x{i}'] = cost
            
            qp.minimize(linear=linear)
            
            # Constraint: select exactly one path
            qp.linear_constraint(
                linear={f'x{i}': 1 for i in range(len(all_paths))},
                sense='==',
                rhs=1
            )
            
            # Solve with QAOA
            qaoa = QAOA(sampler=self.sampler, optimizer=self.optimizer, reps=num_layers)
            optimizer = MinimumEigenOptimizer(qaoa)
            result = optimizer.solve(qp)
            
            # Extract selected path
            selected_idx = None
            for i in range(len(all_paths)):
                if result.x[i] > 0.5:
                    selected_idx = i
                    break
            
            if selected_idx is not None:
                return all_paths[selected_idx], result.fval
            else:
                return all_paths[0], 0.0
                
        except Exception as e:
            print(f"QAOA traversal failed: {e}, falling back to classical")
            return self.classical_traversal(start_node, target_node)
    
    def classical_traversal(self, start_node: str, target_node: str) -> Tuple[List[str], float]:
        """
        Classical shortest path with semantic coherence
        
        Args:
            start_node: Starting node
            target_node: Target node
            
        Returns:
            Tuple of (path, cost)
        """
        try:
            # Use Dijkstra with coherence-weighted edges
            def weight_func(u, v, d):
                base_weight = d.get('weight', 1.0)
                return 1.0 / (base_weight + 0.01)  # Invert for shortest path
            
            path = nx.shortest_path(
                self.graph, start_node, target_node, weight=weight_func
            )
            coherence = self.compute_semantic_coherence(path)
            cost = len(path) * (1.0 - coherence)
            
            return path, cost
        except nx.NetworkXNoPath:
            return [start_node], 0.0
    
    def traverse(self, start_node: str, target_node: str, 
                 use_citations: bool = True) -> Dict:
        """
        Main traversal method with quantum/classical routing
        
        Args:
            start_node: Starting node
            target_node: Target node
            use_citations: Whether to include citation walk
            
        Returns:
            Traversal result dictionary
        """
        start_time = time.time()
        
        # Perform traversal
        if self.use_quantum:
            path, cost = self.qaoa_traversal(start_node, target_node)
            method = 'quantum_qaoa'
        else:
            path, cost = self.classical_traversal(start_node, target_node)
            method = 'classical_dijkstra'
        
        # Add citation walk if requested
        citations = []
        if use_citations and path:
            citations = self.citation_walk(path[-1], max_depth=2)
        
        # Compute metrics
        coherence = self.compute_semantic_coherence(path)
        latency = time.time() - start_time
        
        return {
            'path': path,
            'citations': citations,
            'cost': cost,
            'coherence': coherence,
            'method': method,
            'latency_ms': latency * 1000,
            'path_length': len(path)
        }


def traverse_graph(context: Dict, graph: Optional[nx.Graph] = None) -> Dict:
    """
    Convenience function for graph traversal
    
    Args:
        context: Context dictionary with start/target nodes
        graph: Optional graph (creates demo graph if not provided)
        
    Returns:
        Traversal result
    """
    if graph is None:
        # Create demo graph
        graph = nx.Graph()
        graph.add_edge('A', 'B', weight=0.8, type='semantic')
        graph.add_edge('B', 'C', weight=0.9, type='citation')
        graph.add_edge('A', 'C', weight=0.6, type='semantic')
    
    traversal = QuantumGraphTraversal(graph, use_quantum=True)
    start = context.get('start_node', 'A')
    target = context.get('target_node', 'C')
    
    return traversal.traverse(start, target)
