# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Literal, Optional

class MetricianOutput(BaseModel):
    """Structured output for the Metrician Agent."""
    variance_level: str = Field(description="Description of the variance level (e.g. 'High', 'Low', 'Critical')")
    xg_diff: float = Field(description="Difference between expected goals and actual goals")
    verdict: str = Field(description="Summary verdict: CRITICAL OVERPERFORMANCE / STABLE / REGRESSION LIKELY")
    reasoning: str = Field(description="Detailed statistical reasoning")

class TacticianOutput(BaseModel):
    """Structured output for the Tactician Agent."""
    tactical_advantage: Literal["HOME", "AWAY", "NEUTRAL"] = Field(description="Which team has the tactical upper hand")
    key_battle: str = Field(description="The decisive tactical battle description")
    verdict_summary: str = Field(description="Summary of the tactical analysis")

class OrchestratorOutput(BaseModel):
    """Structured output for the Orchestrator Agent (The Oracle)."""
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    winner_prediction: Literal["HOME", "DRAW", "AWAY"] = Field(description="Predicted outcome")
    logic_summary: str = Field(description="Chronological narrative of the most likely scenario")
    decisive_factor: str = Field(description="The one thing that will decide the match")

class ValueHunterOutput(BaseModel):
    """Structured output for the Value Hunter Agent."""
    ev_percentage: float = Field(description="Expected Value percentage (e.g. 0.05 for 5%)")
    bet_recommendation: str = Field(description="The selection to bet on (e.g. 'Arsenal Win')")
    stake_unit: int = Field(description="Recommended stake units (1-10)", ge=1, le=10)
    reasoning: str = Field(description="Explanation of the edge over the market")

class DispatcherOutput(BaseModel):
    """Structured output for the Dispatcher Agent (Agent 0)."""
    match_found: bool = Field(description="True if a clear match is identified, False otherwise")
    match_id: Optional[str] = Field(default=None, description="Standardized ID: Home_Away_YYYY-MM-DD_Competition (e.g. Arsenal_Liverpool_2026-02-04_PL)")
    home: Optional[str] = Field(default=None, description="Home Team normalized name")
    away: Optional[str] = Field(default=None, description="Away Team normalized name")
    date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    competition: Optional[str] = Field(default=None, description="Competition Code or Name (e.g. PL, LaLiga)")
    reasoning: str = Field(description="Reasoning for selection or clarification question if not found")
