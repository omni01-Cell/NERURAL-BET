# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
import asyncio
import random
from typing import Dict, Any

from src.core.data_provider import MatchDataProvider

class DataMinerAgent(BaseAgent):
    """
    Agent responsible for fetching raw match data (Stats, Lineups, H2H).
    Now enforces a provider via Dependency Injection.
    """
    
    def __init__(self, provider: MatchDataProvider):
        super().__init__(name="Miner_01", role="Data Mining")
        self.provider = provider

    async def process(self, state: AgentState) -> AgentState:
        # Fetch from Provider
        data = await self.provider.get_match_stats(state.match_id)
        
        if not data:
            raise ValueError("Provider returned no data.")

        state.match_data = data
        return state
