# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class NewsDataProvider(ABC):
    """
    Abstract Interface for Football News Providers.
    """
    
    @abstractmethod
    async def get_team_news(self, team_name: str) -> List[Dict[str, Any]]:
        """
        Fetch recent news headlines and snippets for a specific team.
        """
        pass

class MockNewsProvider(NewsDataProvider):
    """
    Simulated news for testing.
    """
    async def get_team_news(self, team_name: str) -> List[Dict[str, Any]]:
        # Simulation: Arsenal has injury issues, Liverpool is flying.
        if "Arsenal" in team_name:
            return [
                {"title": "Odegaard injury doubt for weekend clash", "source": "BBC Sport", "sentiment": "negative"},
                {"title": "Arteta calls for focus ahead of title decider", "source": "Sky", "sentiment": "neutral"}
            ]
        elif "Liverpool" in team_name:
             return [
                {"title": "Salah extends scoring run to 10 games", "source": "Echo", "sentiment": "positive"},
                {"title": "Full squad available for Klopp's successor", "source": "Goal", "sentiment": "positive"}
            ]
        else:
            return []
