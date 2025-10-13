# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Evaluation harness and benchmarking

This module provides:
- BenchmarkHarness: Comprehensive performance benchmarking
- CrossLingualAlignmentScorer: Cross-lingual semantic alignment
- LayerBalanceTest: Context layer validation
"""

from .benchmark_harness import (
    BenchmarkHarness,
    BenchmarkResult,
    run_benchmark,
)

from .alignment_score import (
    CrossLingualAlignmentScorer,
    AlignmentResult,
    compute_alignment_score,
)

from .layer_balance_test import (
    LayerBalanceTest,
    LayerBalanceMetrics,
    create_test_router_with_data,
    run_layer_balance_test,
)

__all__ = [
    # Benchmark Harness
    'BenchmarkHarness',
    'BenchmarkResult',
    'run_benchmark',
    
    # Alignment Scorer
    'CrossLingualAlignmentScorer',
    'AlignmentResult',
    'compute_alignment_score',
    
    # Layer Balance Test
    'LayerBalanceTest',
    'LayerBalanceMetrics',
    'create_test_router_with_data',
    'run_layer_balance_test',
]
