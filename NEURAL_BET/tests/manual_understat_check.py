import asyncio
import aiohttp
from understat import Understat
import json

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        # Search for a team to get ID or name normalization
        print("Searching for Arsenal...")
        teams = await understat.get_teams("epl", 2024) 
        # Note: understat usually returns a list of dicts for teams in a league
        
        target_team = next((t for t in teams if t['title'] == 'Arsenal'), None)
        
        if target_team:
            print(f"Found Arsenal: {target_team}")
            # Get results/fixtures
            print("Fetching results...")
            results = await understat.get_team_results("Arsenal", 2024)
            print(f"Total entries: {len(results) if results else 0}")
            if results:
                print("Last entry:", results[-1])
                print("First entry:", results[0])
                
                # Check for 'isResult' or similar flags indicating played vs fixture
                future = [r for r in results if r.get('isResult') == False or r.get('result') is None]
                print(f"Future matches found: {len(future)}")
                if future:
                    print("Example future match:", future[0])
        else:
            print("Arsenal not found in EPL 2024 list.")

if __name__ == "__main__":
    asyncio.run(main())
