# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.market_provider import MarketDataProvider, MockMarketProvider

class MarketAgent(BaseAgent):
    """
    The Bookie Watcher (Branch B).
    Responsibility: Gather market data (Cotes) in parallel to the analysis.
    This data IS NOT used by Metrician/Tactician (Double Blind).
    """
    
    def __init__(self, provider: MarketDataProvider = None):
        super().__init__(name="Market_01", role="Odds Scraper")
        if provider:
            self.provider = provider
        else:
            self.provider = MockMarketProvider()

    async def process(self, state: AgentState) -> AgentState:
        odds = await self.provider.get_odds(state.match_id)
        if odds:
            state.market_data = odds
        else:
            self.log("No odds found for this match.", level="warning")
            
        return state
