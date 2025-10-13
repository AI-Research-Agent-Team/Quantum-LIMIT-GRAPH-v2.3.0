#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Quick Start Script for Quantum LIMIT-GRAPH v2.3.0
Runs a minimal example to verify installation
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required = [
        ('numpy', 'NumPy'),
        ('networkx', 'NetworkX'),
        ('transformers', 'Transformers'),
        ('torch', 'PyTorch'),
    ]
    
    missing = []
    for module, name in required:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (missing)")
            missing.append(name)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed\n")
    return True


def run_minimal_example():
    """Run a minimal example"""
    print("="*60)
    print("Quantum LIMIT-GRAPH v2.3.0 - Quick Start")
    print("="*60)
    
    # Import modules
    print("\n[1/5] Importing modules...")
    try:
        from src.agent.multilingual_parser import parse_query
        from src.graph.quantum_traversal import traverse_graph
        from src.context.ace_context_router import route_context
        from src.agent.repair_edit_stream import apply_edits
        import networkx as nx
        import numpy as np
        print("  ✓ Modules imported successfully")
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    # Parse query
    print("\n[2/5] Parsing multilingual query...")
    try:
        query = "What is quantum computing?"
        result = parse_query(query, 'en')
        print(f"  ✓ Query parsed: {result['language']} -> {result['subgraph']}")
    except Exception as e:
        print(f"  ✗ Parsing failed: {e}")
        return False
    
    # Route context
    print("\n[3/5] Routing context...")
    try:
        query_emb = np.random.randn(768)
        query_emb = query_emb / np.linalg.norm(query_emb)
        context = route_context(result, query_emb)
        print(f"  ✓ Context routed across {len(context['routed_context'])} layers")
    except Exception as e:
        print(f"  ✗ Context routing failed: {e}")
        return False
    
    # Traverse graph
    print("\n[4/5] Traversing semantic graph...")
    try:
        # Create minimal graph
        G = nx.Graph()
        G.add_edge('A', 'B', weight=0.8, type='semantic')
        G.add_edge('B', 'C', weight=0.9, type='citation')
        
        context['start_node'] = 'A'
        context['target_node'] = 'C'
        traversal = traverse_graph(context, G)
        print(f"  ✓ Path found: {' -> '.join(traversal['path'])}")
        print(f"  ✓ Coherence: {traversal['coherence']:.3f}")
    except Exception as e:
        print(f"  ✗ Traversal failed: {e}")
        return False
    
    # Apply edits
    print("\n[5/5] Applying REPAIR edits...")
    try:
        final = apply_edits(traversal)
        print(f"  ✓ Edits applied: {len(final['edits_applied'])}")
        print(f"  ✓ Reliability: {final['reliability_score']:.3f}")
    except Exception as e:
        print(f"  ✗ Edit application failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ Quick Start Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run full sample: python sample_quantum_limit-graph.py")
    print("  2. Run tests: python test_complete_integration.py")
    print("  3. Run benchmarks: python src/evaluation/benchmark_harness.py")
    print("  4. Explore notebook: jupyter notebook notebooks/demo_quantum_limit_graph.ipynb")
    print("="*60)
    
    return True


def main():
    """Main entry point"""
    print("\nQuantum LIMIT-GRAPH v2.3.0 - Quick Start\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run example
    success = run_minimal_example()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
