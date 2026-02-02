import asyncio
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider
from src.providers.understat_provider import UnderstatProvider
from src.providers.fbref_provider import FBRefProvider

class NeuralBetProvider(MatchDataProvider):
    """
    The Production Provider.
    Aggregates data from Understat (xG) and FBRef (General Stats).
    """
    
    def __init__(self):
        self.understat = UnderstatProvider()
        self.fbref = FBRefProvider()

    async def get_match_stats(self, match_id: str) -> Optional[Dict[str, Any]]:
        # Format: "HomeTeam_AwayTeam_Date_League"
        # e.g. "Arsenal_Liverpool_2026_PL"
        # Defaults to PL if not specified.
        
        try:
            parts = match_id.split("_")
            if len(parts) < 2:
                return {"error": "Invalid Match ID format. Use Home_Away[_Date_League]"}
            
            home_team = parts[0]
            away_team = parts[1]
            # Try to grab league from last part if it matches standard codes
            # This is a basic heuristic for MVP
            league_code = "PL"
            if len(parts) >= 4:
                possible_league = parts[3].upper()
                if possible_league in ["PL", "LIGA", "SERIE_A", "BUNDESLIGA", "L1"]:
                   league_code = possible_league
            
            # Parallel Fetch
            # 1. Understat Form (Understat usually manages leagues internally or we might need to add league arg there too later)
            home_us_task = self.understat.get_team_form(home_team)
            away_us_task = self.understat.get_team_form(away_team)
            
            # 2. FBRef Stats (Now with League injection)
            home_fb_task = self.fbref.get_team_form(home_team, league=league_code)
            away_fb_task = self.fbref.get_team_form(away_team, league=league_code)
            
            results = await asyncio.gather(home_us_task, away_us_task, home_fb_task, away_fb_task, return_exceptions=True)
            
            home_us, away_us, home_fb, away_fb = results
            
            # Construct the Rich Data Object
            return {
                "id": match_id,
                "home_team": home_team,
                "away_team": away_team,
                "stats": {
                    "home": {
                        "understat_form": home_us if not isinstance(home_us, Exception) else "Error",
                        "fbref_stats": home_fb if not isinstance(home_fb, Exception) else "Error"
                    },
                    "away": {
                        "understat_form": away_us if not isinstance(away_us, Exception) else "Error",
                        "fbref_stats": away_fb if not isinstance(away_fb, Exception) else "Error"
                    }
                },
                "meta": {
                    "provider": "NeuralBet Hybrid (Understat + FBRef)"
                }
            }
            
        except Exception as e:
            return {"error": f"Hybrid Fetch Failed: {str(e)}"}

    async def get_team_form(self, team_id: str, last_n: int = 5) -> Dict[str, Any]:
        return await self.understat.get_team_form(team_id, last_n)
