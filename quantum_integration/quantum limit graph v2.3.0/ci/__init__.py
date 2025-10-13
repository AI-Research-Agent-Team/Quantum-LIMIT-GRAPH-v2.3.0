# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 AI Research Agent Team

"""
CI/CD integration and validation

This module provides:
- EditStreamValidator: Edit stream integrity testing
- SPDXChecker: License compliance verification
"""

from .validator import (
    EditStreamValidator,
    ValidationResult,
    run_validation,
)

from .spdx_checker import (
    SPDXChecker,
    SPDXCheckResult,
    check_spdx_compliance,
)

__all__ = [
    # Edit Stream Validator
    'EditStreamValidator',
    'ValidationResult',
    'run_validation',
    
    # SPDX Checker
    'SPDXChecker',
    'SPDXCheckResult',
    'check_spdx_compliance',
]
