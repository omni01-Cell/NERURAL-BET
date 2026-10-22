# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MarketDataProvider(ABC):
    """
    Abstract Interface for Betting Odds Providers.
    """
    
    @abstractmethod
    async def get_odds(self, match_id: str) -> Optional[Dict[str, float]]:
        """
        Fetch standard odds (1X2, BTTS, Over/Under).
        Returns a dictionary like:
        {
            "home_win": 1.95,
            "draw": 3.60,
            "away_win": 4.10,
            "over_2_5": 1.70,
            "btts_yes": 1.65
        }
        """
        pass

class MockMarketProvider(MarketDataProvider):
    """
    Simulated market for testing Value Hunter logic.
    """
    async def get_odds(self, match_id: str) -> Optional[Dict[str, float]]:
        # Simulation: Market favors Arsenal heavily against Liverpool? 
        return {
            "home_win": 2.10,
            "draw": 3.50,
            "away_win": 3.20,
            "over_2_5": 1.65,
            "btts_yes": 1.55
        }
