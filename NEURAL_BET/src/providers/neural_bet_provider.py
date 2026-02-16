import asyncio
from typing import Dict, Any, Optional
from src.core.data_provider import MatchDataProvider
from src.providers.understat_provider import UnderstatProvider
from src.providers.fbref_provider import FBRefProvider
import logging

logger = logging.getLogger(__name__)


class NeuralBetProvider(MatchDataProvider):
    """
    The Production Provider.
    Aggregates data from Understat (xG) and FBRef (General Stats).
    
    Implements async context manager for proper resource cleanup.
    
    Usage:
        async with NeuralBetProvider() as provider:
            data = await provider.get_match_stats(match_id)
    """
    
    def __init__(self):
        self.understat = UnderstatProvider()
        self.fbref = FBRefProvider()

    async def __aenter__(self) -> "NeuralBetProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - ensures cleanup of child providers."""
        await self.close()

    async def close(self) -> None:
        """Close all child provider sessions."""
        await self.understat.close()
        logger.debug("NeuralBetProvider closed")

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

    async def find_next_match(self, team_name: str, opponent_name: Optional[str] = None, date_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Dispatcher V3 (Real Verification):
        1. Query Understat for the REAL next fixture for 'team_name'.
        2. If found:
           - Check if opponent matches (fuzzy match).
           - Return the OFFICIAL date and league.
        3. If not found (or scraping fails):
           - If user provided a date, trust it (Fallback).
           - If no date, FAIL.
        """
        from datetime import datetime
        
        # 1. Try Real Verification
        real_fixture = await self.understat.get_next_fixture(team_name)
        
        if real_fixture:
            # ... (Understat logic kept as is) ...
            # Check opponent match if provided
            scraped_opponent = real_fixture['opponent']
            scraped_date = real_fixture['date']
            
            is_opponent_match = True
            if opponent_name:
                t1 = opponent_name.lower().replace("fc", "").strip()
                t2 = scraped_opponent.lower().replace("fc", "").strip()
                is_opponent_match = (t1 in t2) or (t2 in t1)
            
            if is_opponent_match:
                return {
                    "found": True,
                    "home": team_name,
                    "away": scraped_opponent,
                    "date": scraped_date,
                    "league": "PL", 
                    "match_id": f"{team_name}_{scraped_opponent}_{scraped_date}_PL".replace(" ", "_"),
                    "source": "Understat (Verified)"
                }
            else:
                return {
                    "found": False,
                    "reason": f"Next match for {team_name} is vs {scraped_opponent} on {scraped_date}, NOT {opponent_name}."
                }

        # 2. Fallback: Check FBRef for Championship/Other Teams (Partial Verification)
        # If Understat missed it, maybe it's a Championship team?
        # 2. Fallback: Check FBRef for Championship/Other Teams (Partial Verification)
        fbref_reason = "Not attempted"
        try:
             # Try verifying existence in Championship
             fbreq = await self.fbref.get_team_form(team_name, league="CHAMPIONSHIP")
             
             if "error" not in fbreq:
                 # Team exists in Championship!
                 if date_hint:
                     return {
                        "found": True,
                        "home": team_name,
                        "away": opponent_name or "Unknown",
                        "date": date_hint,
                        "league": "CHAMPIONSHIP",
                        "match_id": f"{team_name}_{opponent_name}_{date_hint}_CHAMPSHIP".replace(" ", "_"),
                        "source": "FBRef Only (Team Verified, Date User-Provided)"
                     }
                 else:
                     fbref_reason = "Team found in FBRef Championship, but NO DATE provided by user."
             else:
                 fbref_reason = f"FBRef Error: {fbreq['error']}"
        except Exception as e:
            fbref_reason = f"FBRef Exception: {str(e)}"

        # 3. Last Resort: Handling Verification Failures
        # If we reached here, it means:
        # A. Understat failed (or didn't find match).
        # B. FBRef failed (Error/403) or didn't find match.
        
        if date_hint:
             # SOFT FAIL: If providers are blocked/down (403), we TRUST the user.
             # We shouldn't block the valid request just because our scraper is blocked.
             reason_short = "Provider Blocked/Error"
             if "403" in fbref_reason:
                 reason_short = "FBRef Blocked (403)"
                 
             return {
                "found": True,
                "home": team_name,
                "away": opponent_name or "Unknown",
                "date": date_hint,
                "league": "UNK", 
                "match_id": f"{team_name}_{opponent_name}_{date_hint}_UNK".replace(" ", "_"),
                "source": f"User Input ({reason_short})"
             }

        # 4. Fail - Truly stuck (No verification AND No user date)
        return {
            "found": False,
            "reason": f"Could not verify next match for {team_name}. Understat: Scrape Failed. FBRef: {fbref_reason}. Please specify a date."
        }
