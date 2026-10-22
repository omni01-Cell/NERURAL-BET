import soccerdata as sd
import pandas as pd
from datetime import datetime

def main():
    print("Initializing soccerdata FBref for Championship 2024...") # usually '2024' covers 24/25
    try:
        # Trying to initialize specific league
        fb = sd.FBref(leagues="ENG-Championship", seasons="2024")
        
        print("Fetching schedule...")
        schedule = fb.read_schedule()
        
        print(f"Schedule fetched with {len(schedule)} rows.")
        
        # Filter for upcoming matches (date > now)
        now = pd.Timestamp.now()
        upcoming = schedule[schedule['date'] > now]
        upcoming = upcoming.sort_values(by='date')
        
        print(f"Upcoming matches found: {len(upcoming)}")
        
        # Check for Blackburn
        team_name = "Blackburn"
        blackburn_games = upcoming[
            (upcoming['home_team'].str.contains(team_name, case=False, na=False)) | 
            (upcoming['away_team'].str.contains(team_name, case=False, na=False))
        ]
        
        if not blackburn_games.empty:
            print("Found Blackburn upcoming match:")
            next_game = blackburn_games.iloc[0]
            print(f"{next_game['home_team']} vs {next_game['away_team']} on {next_game['date']}")
        else:
            print("No upcoming Blackburn matches found in fetched schedule.")
            
    except Exception as e:
        print(f"Soccerdata Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("Required libraries missing? (pandas, lxml, html5lib)")
