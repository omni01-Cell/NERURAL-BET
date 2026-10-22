# -*- coding: utf-8 -*-
import asyncio
import aiohttp
from understat import Understat
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider
import logging

logger = logging.getLogger(__name__)


class UnderstatProvider(MatchDataProvider):
    """
    Provider for Understat (xG, xGA, xPoints).
    Implements async context manager for proper session cleanup.
    
    Usage:
        async with UnderstatProvider() as provider:
            data = await provider.get_team_form("Arsenal")
    """
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._owns_session = session is None  # Track if we created the session
        self.understat = None

    async def __aenter__(self) -> "UnderstatProvider":
        """Async context manager entry."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - ensures cleanup."""
        await self.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
            self.understat = Understat(self._session)
        elif not self.understat:
            self.understat = Understat(self._session)
        return self._session

    async def close(self) -> None:
        """Close session if we own it. Safe to call multiple times."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()
            logger.debug("UnderstatProvider session closed")
        self._session = None
        self.understat = None

    def __del__(self):
        """Safety net - warn if session wasn't closed properly."""
        if self._owns_session and self._session and not self._session.closed:
            logger.warning(
                "UnderstatProvider session not closed! Use 'async with' or call close() explicitly."
            )

    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        return None 

    @property
    def _cached_get_team_form(self):
        """Lazy import to avoid circular imports."""
        from src.core.cache import cached
        return cached

    async def get_team_form(self, team_name: str, last_n: int = 5) -> Dict[str, Any]:
        """Get team form with caching (5 min TTL)."""
        # Check cache first via wrapper
        return await self._get_team_form_impl(team_name, last_n)
    
    async def _get_team_form_impl(self, team_name: str, last_n: int = 5) -> Dict[str, Any]:
        """Internal implementation of get_team_form."""
        from src.core.cache import get_cache
        
        cache = get_cache()
        cache_key = cache._make_key("understat_team_form", team_name, last_n)
        
        # Try cache
        cached_result = await cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        await self._get_session()
        
        try:
            data = await self.understat.get_team_results(team_name, 2024)
            
            if not data:
                return {"error": f"No data for {team_name}"}

            recent_games = data[-last_n:]
            
            total_xg = sum(float(g['xG']) for g in recent_games)
            total_xga = sum(float(g['xGA']) for g in recent_games)
            
            result = {
                "source": "Understat",
                "team": team_name,
                "matches_analyzed": len(recent_games),
                "total_xg": round(total_xg, 2),
                "total_xga": round(total_xga, 2),
                "avg_xg": round(total_xg / len(recent_games), 2),
                "avg_xga": round(total_xga / len(recent_games), 2),
                "last_match_result": recent_games[-1]['result']
            }
            
            # Cache successful result (5 min TTL)
            await cache.set(cache_key, result, ttl=300)
            return result
            
        except Exception as e:
            return {"error": str(e)}

    async def get_next_fixture(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrapes Understat team page to find the next scheduled match.
        This provides REAL verification of the match existence.
        
        Returns:
            {
                "date": "2026-02-04",
                "opponent": "Liverpool",
                "home_away": "h",
                "id": "12345"
            }
        """
        await self._get_session()
        import re
        import json
        from datetime import datetime
        
        url = f"https://understat.com/team/{team_name.replace(' ', '_')}/2024" # 2024 covers 2024/2025 season usually? Or check year.
        # Understat year logic: 2024 starts Aug 2024. 2025 starts Aug 2025.
        # Assuming current season is 2025 (user context says 2026-02-02).
        # We might need to check multiple years if end of season.
        # For now, let's try 2025 based on date.
        
        # User date is Feb 2026 -> Season 2025/2026 -> Understat "2025".
        season_year = 2025 
        url = f"https://understat.com/team/{team_name.replace(' ', '_')}/{season_year}"
        
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                
                # Regex to find datesData
                # var datesData = JSON.parse('...');
                match = re.search(r"var datesData\s*=\s*JSON\.parse\('([^']+)'\)", html)
                if match:
                    json_str = match.group(1).encode('utf-8').decode('unicode_escape')
                    fixtures = json.loads(json_str)
                    
                    # Filter for unplayed matches (isResult = False)
                    upcoming = [f for f in fixtures if f.get('isResult') is False]
                    
                    if upcoming:
                        # Sort by date just in case
                        upcoming.sort(key=lambda x: x['datetime'])
                        
                        next_match = upcoming[0]
                        opponent_name = next_match['a']['title'] if next_match['h']['title'] == team_name else next_match['h']['title']
                        
                        return {
                            "date": next_match['datetime'].split(' ')[0], # YYYY-MM-DD
                            "opponent": opponent_name,
                            "home_away": next_match['side'],
                            "id": next_match['id'],
                            "competition": "PL" # Default to PL as Understat is PL centric in this scraping or we'd need to parse league from page
                        }
        except Exception as e:
            print(f"Understat Scrape Error: {e}")
            return None
        return None
        # DELETED finally: await self.close() -> Proper resource management
