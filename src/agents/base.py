# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
import logging

# Configure Logger
logger = logging.getLogger(__name__)

class AgentState(BaseModel):
    """
    Shared state object passed between agents strictly typed.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    match_id: str
    match_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    analysis_reports: Dict[str, Any] = {}
    errors: list[str] = []

class BaseAgent(ABC):
    """
    Abstract Base Class for all Neural Bet Agents.
    Enforces a strict 'process' method contract.
    
    Attributes:
        is_critical: If True, agent failure stops the pipeline.
                     If False, pipeline continues in degraded mode.
    """
    
    # Default: agents are CRITICAL (pipeline stops on failure)
    is_critical: bool = True
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.logger.setLevel(logging.INFO)

    async def execute(self, state: AgentState) -> AgentState:
        """
        Standardized execution wrapper with built-in error handling and logging.
        
        STATE HANDLING PATTERN:
        - Input state is treated as IMMUTABLE (not modified in place)
        - Returns a NEW AgentState with modifications
        - This prevents confusion about mutation vs return semantics
        
        Critical agents raise CriticalAgentError on failure (fail-fast).
        Non-critical agents append error and continue (degraded mode).
        
        Args:
            state: Input state (treated as read-only)
            
        Returns:
            New AgentState with this agent's modifications
        """
        self.log(f"Starting operation for {state.match_id}...")
        
        # Create a working copy to avoid mutation confusion
        # Note: model_copy() is Pydantic v2's way to copy models
        working_state = state.model_copy(deep=True)
        
        try:
            # Subclasses implement their logic in 'process'
            # They receive and return the working copy
            result_state = await self.process(working_state)
            self.log("Operation completed successfully.")
            return result_state
            
        except Exception as e:
            error_msg = f"{self.name} Error: {str(e)}"
            self.log(error_msg, level="error")
            working_state.errors.append(error_msg)
            
            # CRITICAL agents stop the pipeline immediately
            if self.is_critical:
                from src.core.exceptions import CriticalAgentError
                raise CriticalAgentError(
                    f"Critical agent '{self.name}' failed: {str(e)}",
                    code="CRITICAL_AGENT_FAILURE",
                    details={"agent": self.name, "role": self.role, "original_error": str(e)}
                ) from e
            
            # Non-critical agents log warning and continue with error appended
            self.log("Continuing in degraded mode (non-critical agent)...", level="warning")
            return working_state

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Core logic implemented by each specialized agent.
        
        CONTRACT:
        - Receives a mutable state copy (safe to modify)
        - MUST return the modified state
        - Should not maintain references to state after returning
        """
        pass

    def log(self, message: str, level: str = "info"):
        """Standardized logging header for agents."""
        prefix = f"[{self.role.upper()}::{self.name}]"
        if level == "error":
            self.logger.error(f"{prefix} {message}")
        elif level == "warning":
            self.logger.warning(f"{prefix} {message}")
        else:
            self.logger.info(f"{prefix} {message}")
