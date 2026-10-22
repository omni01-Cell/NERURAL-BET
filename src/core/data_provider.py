# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MatchDataProvider(ABC):
    """
    Abstract Interface for Football Data Providers.
    Allows switching between Mock, FBRef, API-Football, etc.
    """
    
    @abstractmethod
    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_team_form(self, team_id: str, last_n: int = 5) -> Dict[str, Any]:
        pass

class MockProvider(MatchDataProvider):
    """
    Simulated provider for testing/development.
    """
    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        return {
            "id": match_id,
            "home_team": "Arsenal", 
            "away_team": "Liverpool",
            "xg_home": 1.85,
            "xg_away": 1.42,
            "possession_home": 55,
            "possession_away": 45
        }

    async def get_team_form(self, team_id: str, last_n: int = 5) -> Dict[str, Any]:
        return {
            "team": team_id,
            "wins": 4,
            "losses": 0,
            "draws": 1,
            "avg_xg": 2.1,
            "avg_xga": 0.8
        }
