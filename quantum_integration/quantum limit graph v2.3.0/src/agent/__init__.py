# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
Agent modules for multilingual processing and repair

This module provides:
- MultilingualParser: mBART-50 based multilingual parsing with 15+ languages
- REPAIREditStream: Hallucination detection and correction with dual-memory
"""

from .multilingual_parser import (
    MultilingualParser,
    parse_query,
)

from .repair_edit_stream import (
    REPAIREditStream,
    EditType,
    HallucinationType,
    Edit,
    MemoryEntry,
    apply_edits,
)

__all__ = [
    # Multilingual Parser
    'MultilingualParser',
    'parse_query',
    
    # REPAIR Edit Stream
    'REPAIREditStream',
    'EditType',
    'HallucinationType',
    'Edit',
    'MemoryEntry',
    'apply_edits',
]
