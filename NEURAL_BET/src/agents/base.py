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
    analysis_reports: Dict[str, str] = {}
    errors: list[str] = []

class BaseAgent(ABC):
    """
    Abstract Base Class for all Neural Bet Agents.
    Enforces a strict 'process' method contract.
    """
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(f"agent.{name.lower()}")
        self.logger.setLevel(logging.INFO)

    async def execute(self, state: AgentState) -> AgentState:
        """
        Standardized execution wrapper with built-in error handling and logging.
        This follows the Template Method pattern core part.
        """
        self.log(f"Starting operation for {state.match_id}...")
        try:
            # Subclasses implement their logic in 'process'
            state = await self.process(state)
            self.log("Operation completed successfully.")
        except Exception as e:
            error_msg = f"{self.name} Error: {str(e)}"
            self.log(error_msg, level="error")
            state.errors.append(error_msg)
            # We don't raise here to allow the pipeline to continue (Degraded mode)
        
        return state

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """
        Core logic implemented by each specialized agent.
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
