# -*- coding: utf-8 -*-
"""
Quantum LIMIT-GRAPH v2.3.0 - Complete Integration Sample
Demonstrates multilingual quantum research agent with LIMIT-GRAPH
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.agent.multilingual_parser import parse_query
from src.graph.quantum_traversal import traverse_graph
from src.context.ace_context_router import route_context
from src.agent.repair_edit_stream import apply_edits
import networkx as nx
import numpy as np

def create_demo_graph():
    """Create demo semantic graph"""
    G = nx.Graph()
    
    # Add nodes with multilingual content
    nodes = [
        ('quantum_ml', 'Quantum Machine Learning'),
        ('qaoa', 'Quantum Approximate Optimization Algorithm'),
        ('vqe', 'Variational Quantum Eigensolver'),
        ('qnn', 'Quantum Neural Networks'),
        ('hybrid_algo', 'Hybrid Quantum-Classical Algorithms')
    ]
    
    for node_id, label in nodes:
        G.add_node(node_id, label=label)
    
    # Add edges with weights
    edges = [
        ('quantum_ml', 'qaoa', 0.85, 'semantic'),
        ('quantum_ml', 'qnn', 0.90, 'semantic'),
        ('qaoa', 'hybrid_algo', 0.80, 'citation'),
        ('vqe', 'hybrid_algo', 0.75, 'citation'),
        ('qnn', 'hybrid_algo', 0.88, 'semantic')
    ]
    
    for src, dst, weight, edge_type in edges:
        G.add_edge(src, dst, weight=weight, type=edge_type)
    
    return G

def main():
    """Main execution flow"""
    print("="*60)
    print("Quantum LIMIT-GRAPH v2.3.0 - Multilingual Research Agent")
    print("="*60)
    
    # Step 1: Parse multilingual query
    query = "Apa perkembangan terbaru dalam pembelajaran mesin kuantum?"
    lang = "id"  # Indonesian
    
    print(f"\n1. Parsing Query (Language: {lang})")
    print(f"   Query: {query}")
    
    tokens = parse_query(query, lang)
    print(f"   ✓ Detected Language: {tokens['language']}")
    print(f"   ✓ Subgraph Route: {tokens['subgraph']}")
    print(f"   ✓ Normalized: {tokens['normalized']}")
    
    # Step 2: Route context through ACE layers
    print(f"\n2. Routing Context through ACE Layers")
    
    # Create query embedding
    query_embedding = np.random.randn(768)
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    
    context = route_context(tokens, query_embedding)
    print(f"   ✓ Context routed across {len(context['routed_context'])} layers")
    print(f"   ✓ Layer stats: {context['layer_stats']}")
    
    # Step 3: Quantum graph traversal
    print(f"\n3. Quantum Graph Traversal (QAOA)")
    
    demo_graph = create_demo_graph()
    context['start_node'] = 'quantum_ml'
    context['target_node'] = 'hybrid_algo'
    
    traversal_path = traverse_graph(context, demo_graph)
    print(f"   ✓ Method: {traversal_path['method']}")
    print(f"   ✓ Path: {' -> '.join(traversal_path['path'])}")
    print(f"   ✓ Coherence: {traversal_path['coherence']:.3f}")
    print(f"   ✓ Latency: {traversal_path['latency_ms']:.2f} ms")
    print(f"   ✓ Citations: {len(traversal_path['citations'])} nodes")
    
    # Step 4: Apply REPAIR edits
    print(f"\n4. Applying REPAIR Edit Stream")
    
    final_output = apply_edits(traversal_path)
    print(f"   ✓ Original: {final_output['original_text']}")
    print(f"   ✓ Edited: {final_output['edited_text']}")
    print(f"   ✓ Edits Applied: {final_output['statistics']['total_edits']}")
    print(f"   ✓ Reliability: {final_output['reliability_score']:.3f}")
    
    if final_output['hallucination_detected']:
        print(f"   ⚠ Hallucination Detected: {final_output['hallucination_detected']}")
    
    # Summary
    print(f"\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    print(f"Language: {tokens['language']} ({tokens['mbart_lang']})")
    print(f"Traversal Method: {traversal_path['method']}")
    print(f"Path Length: {traversal_path['path_length']}")
    print(f"Semantic Coherence: {traversal_path['coherence']:.3f}")
    print(f"Total Latency: {traversal_path['latency_ms']:.2f} ms")
    print(f"Memory Entries: {final_output['statistics']['short_term_entries']} (ST) + {final_output['statistics']['long_term_entries']} (LT)")
    print("="*60)
    
    return final_output

if __name__ == '__main__':
    result = main()
