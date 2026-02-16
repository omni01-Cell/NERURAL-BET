import requests
import json

def search_fotmob(query):
    url = f"https://www.fotmob.com/api/searchData?term={query}"
    print(f"Querying: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Inspect structure
            print("Keys:", data.keys())
            if 'teamData' in data:
                 print(f"Found {len(data['teamData'])} teams.")
                 first_team = data['teamData'][0]
                 print(f"First Team: {first_team['name']} (ID: {first_team['id']})")
                 return first_team['id']
        else:
            print(f"Error {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")
    return None

def get_fixtures(team_id):
    url = f"https://www.fotmob.com/api/teams?id={team_id}&ccode3=USA"
    print(f"Querying Team Details: {url}")
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'fixtures' in data:
                fixtures = data['fixtures']
                print(f"Fixtures found: {len(fixtures)}")
                # Check 'allFixtures' or similar
                # Recent structure changes often, let's dump keys
                # print(data['fixtures'].keys())
                # Usually it's a list or dict with 'upcoming'
                pass
            return data
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    tid = search_fotmob("Blackburn")
    if tid:
        get_fixtures(tid)
