# -*- coding: utf-8 -*-
import pandas as pd
import asyncio
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider

class FBRefProvider(MatchDataProvider):
    """
    Provider for FBRef (Possession, Pressing, etc.).
    Uses Pandas read_html (Scraping).
    WARNING: High risk of Rate Limiting (429).
    """
    
    LEAGUE_URLS = {
        "PL": "https://fbref.com/en/comps/9/Premier-League-Stats",
        "LIGA": "https://fbref.com/en/comps/12/La-Liga-Stats",
        "SERIE_A": "https://fbref.com/en/comps/11/Serie-A-Stats",
        "BUNDESLIGA": "https://fbref.com/en/comps/20/Bundesliga-Stats",
        "L1": "https://fbref.com/en/comps/13/Ligue-1-Stats"
    }

    async def get_team_form(self, team_name: str, last_n: int = 5, league: str = "PL") -> Dict[str, Any]:
        """
        Attempts to fetch general stats from the specified league table.
        Args:
            team_name: Team name (fuzzy matched)
            last_n: Ignored for now (returns seasonal stats)
            league: League Code (PL, LIGA, SERIE_A, BUNDESLIGA, L1)
        """
        url = self.LEAGUE_URLS.get(league, self.LEAGUE_URLS["PL"])
        
        try:
            # We run blocking I/O (pandas) in a thread
            loop = asyncio.get_event_loop()
            tables = await loop.run_in_executor(None, lambda: pd.read_html(url, match="Regular Season"))
            
            if not tables:
                return {"error": "No tables found on FBRef"}
                
            df = tables[0]
            
            # Simple fuzzy match for team name
            # FBRef typical names: "Arsenal", "Liverpool", "Manchester City", "Real Madrid", "Inter"
            row = df[df['Squad'].str.contains(team_name, case=False, na=False)]
            
            if row.empty:
                return {"error": f"Team {team_name} not found in FBRef ({league}) table"}
                
            stats = row.iloc[0]
            
            return {
                "source": "FBRef",
                "league": league,
                "possession_avg": stats.get('Poss', 50.0), # If column exists
                "goals_scored": stats.get('GF', 0),
                "goals_against": stats.get('GA', 0),
                "league_rank": stats.get('Rk', 0)
            }
            
        except Exception as e:
            # Fallback for 429 or other errors
            return {"error": f"FBRef Scraping Failed: {str(e)}"}

    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        return None
