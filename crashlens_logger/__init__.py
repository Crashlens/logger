#!/usr/bin/env python3
"""
CrashLens Logger package initialization.
"""

__version__ = "1.0.0"
__author__ = "CrashLens Team"
__description__ = "CLI tool for generating structured logs of LLM API usage"

from .logger import CrashLensLogger, LogEvent, TokenEstimator, CostCalculator

__all__ = [
    "CrashLensLogger",
    "LogEvent", 
    "TokenEstimator",
    "CostCalculator"
]
