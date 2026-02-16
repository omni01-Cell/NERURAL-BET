# -*- coding: utf-8 -*-
"""
FBRef Provider using soccerdata library.
Handles anti-bot protections automatically via the maintained soccerdata package.
"""
import asyncio
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider
import logging

logger = logging.getLogger(__name__)


class FBRefProvider(MatchDataProvider):
    """
    Provider for FBRef stats using soccerdata library.
    soccerdata handles headers, sessions, and rate limiting properly.
    """
    
    LEAGUE_MAP = {
        "PL": "ENG-Premier League",
        "LIGA": "ESP-La Liga",
        "SERIE_A": "ITA-Serie A",
        "BUNDESLIGA": "GER-Bundesliga",
        "L1": "FRA-Ligue 1",
        "CHAMPIONSHIP": "ENG-Championship",
    }
    
    def __init__(self):
        self._fbref_cache: Dict[str, Any] = {}
    
    def _get_fbref_instance(self, league: str, season: str = "2024"):
        """
        Get or create a cached FBref instance.
        soccerdata manages session/cookies internally.
        """
        import soccerdata as sd
        
        cache_key = f"{league}_{season}"
        if cache_key not in self._fbref_cache:
            league_code = self.LEAGUE_MAP.get(league, self.LEAGUE_MAP["PL"])
            self._fbref_cache[cache_key] = sd.FBref(
                leagues=league_code, 
                seasons=season
            )
        return self._fbref_cache[cache_key]

    async def get_team_form(self, team_name: str, last_n: int = 5, league: str = "PL") -> Dict[str, Any]:
        """
        Fetch team stats from FBRef using soccerdata.
        Runs blocking I/O in executor to keep async.
        """
        loop = asyncio.get_event_loop()
        
        def fetch_stats():
            try:
                fb = self._get_fbref_instance(league)
                
                # Get league table (most reliable data point)
                stats_df = fb.read_league_table()
                
                if stats_df.empty:
                    return {"error": "No league table data from FBRef"}
                
                # Fuzzy match team name (FBRef uses full names like "Arsenal", "Liverpool")
                mask = stats_df.index.get_level_values('team').str.contains(
                    team_name, case=False, na=False
                )
                team_data = stats_df[mask]
                
                if team_data.empty:
                    return {"error": f"Team '{team_name}' not found in FBRef {league}"}
                
                row = team_data.iloc[0]
                
                return {
                    "source": "FBRef (soccerdata)",
                    "league": league,
                    "team": team_name,
                    "matches_played": int(row.get('MP', 0)),
                    "wins": int(row.get('W', 0)),
                    "draws": int(row.get('D', 0)),
                    "losses": int(row.get('L', 0)),
                    "goals_scored": int(row.get('GF', 0)),
                    "goals_against": int(row.get('GA', 0)),
                    "goal_diff": int(row.get('GD', 0)),
                    "points": int(row.get('Pts', 0)),
                    "xG": float(row.get('xG', 0.0)),
                    "xGA": float(row.get('xGA', 0.0)),
                }
                
            except ImportError:
                return {"error": "soccerdata not installed. Run: pip install soccerdata"}
            except Exception as e:
                logger.error(f"FBRef fetch failed: {e}")
                return {"error": f"FBRef Error: {str(e)}"}
        
        return await loop.run_in_executor(None, fetch_stats)

    async def get_team_schedule(self, team_name: str, league: str = "PL") -> Dict[str, Any]:
        """
        Get upcoming matches for a team.
        """
        loop = asyncio.get_event_loop()
        
        def fetch_schedule():
            try:
                import pandas as pd
                fb = self._get_fbref_instance(league)
                
                schedule = fb.read_schedule()
                now = pd.Timestamp.now()
                
                # Filter upcoming matches for this team
                upcoming = schedule[schedule['date'] > now]
                team_matches = upcoming[
                    (upcoming['home_team'].str.contains(team_name, case=False, na=False)) |
                    (upcoming['away_team'].str.contains(team_name, case=False, na=False))
                ].sort_values('date')
                
                if team_matches.empty:
                    return {"error": f"No upcoming matches for {team_name}"}
                
                next_match = team_matches.iloc[0]
                return {
                    "source": "FBRef (soccerdata)",
                    "home_team": next_match['home_team'],
                    "away_team": next_match['away_team'],
                    "date": str(next_match['date']),
                    "league": league,
                }
                
            except Exception as e:
                logger.error(f"FBRef schedule fetch failed: {e}")
                return {"error": f"FBRef Schedule Error: {str(e)}"}
        
        return await loop.run_in_executor(None, fetch_schedule)

    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        FBRef match stats require match-specific URLs.
        For now, returns None - use get_team_form for aggregate stats.
        """
        return None
