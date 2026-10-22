# -*- coding: utf-8 -*-
"""
Custom Exception Hierarchy for Neural Bet.
Provides typed, debuggable exceptions for the agent pipeline.
"""
from datetime import datetime
from typing import Optional, Dict, Any


class NeuralBetError(Exception):
    """Base exception for all Neural Bet errors."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.code:
            return f"[{self.code}] {base}"
        return base


class CriticalAgentError(NeuralBetError):
    """
    Raised when a CRITICAL agent fails.
    Pipeline MUST stop immediately - no recovery possible.
    
    Examples: DataMiner, Metrician, Orchestrator failures.
    """
    pass


class DegradedAgentError(NeuralBetError):
    """
    Raised when a DEGRADABLE agent fails.
    Pipeline can continue without this agent's output.
    
    Examples: DevilsAdvocate, Psych failures.
    """
    pass


class DataProviderError(NeuralBetError):
    """
    Raised when an external data provider fails.
    Should be wrapped by agent-level exceptions.
    
    Examples: API timeout, rate limit, invalid response.
    """
    
    def __init__(
        self, 
        message: str, 
        provider: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code, details)
        self.provider = provider


class ValidationError(NeuralBetError):
    """
    Raised when input validation fails.
    Fail-fast on invalid state.
    """
    pass


class ConfigurationError(NeuralBetError):
    """
    Raised when required configuration is missing or invalid.
    Should fail-fast at startup, not silently continue.
    """
    pass
