# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Graph traversal and semantic operations

This module provides:
- QuantumGraphTraversal: QAOA-based quantum graph traversal
- Classical fallback with Dijkstra algorithm
- Citation walks and semantic coherence scoring
"""

from .quantum_traversal import (
    QuantumGraphTraversal,
    traverse_graph,
)

__all__ = [
    'QuantumGraphTraversal',
    'traverse_graph',
]
