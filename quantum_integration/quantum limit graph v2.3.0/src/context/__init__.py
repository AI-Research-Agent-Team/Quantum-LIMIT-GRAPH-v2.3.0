# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Context routing and ACE integration

This module provides:
- ACEContextRouter: Hierarchical context routing across 3 layers
- Dynamic similarity thresholds (0.70-0.95)
- Context merging and optimization
"""

from .ace_context_router import (
    ACEContextRouter,
    ContextLayer,
    ContextEntry,
    route_context,
)

__all__ = [
    'ACEContextRouter',
    'ContextLayer',
    'ContextEntry',
    'route_context',
]
