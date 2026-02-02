# -*- coding: utf-8 -*-
import asyncio
import aiohttp
from understat import Understat
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider

class UnderstatProvider(MatchDataProvider):
    """
    Provider for Understat (xG, xGA, xPoints).
    Optimized with persistent session management.
    """
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self.understat = None

    async def _get_session(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
            self.understat = Understat(self._session)
        elif not self.understat:
            self.understat = Understat(self._session)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        return None 

    async def get_team_form(self, team_name: str, last_n: int = 5) -> Dict[str, Any]:
        await self._get_session()
        
        try:
            data = await self.understat.get_team_results(team_name, 2024)
            
            if not data:
                return {"error": f"No data for {team_name}"}

            recent_games = data[-last_n:]
            
            total_xg = sum(float(g['xG']) for g in recent_games)
            total_xga = sum(float(g['xGA']) for g in recent_games)
            
            return {
                "source": "Understat",
                "team": team_name,
                "matches_analyzed": len(recent_games),
                "total_xg": round(total_xg, 2),
                "total_xga": round(total_xga, 2),
                "avg_xg": round(total_xg / len(recent_games), 2),
                "avg_xga": round(total_xga / len(recent_games), 2),
                "last_match_result": recent_games[-1]['result']
            }
            
        except Exception as e:
            return {"error": str(e)}
        # DELETED finally: await self.close() -> Proper resource management
