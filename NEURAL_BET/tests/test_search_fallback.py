import requests
import re
from datetime import datetime

def search_ddg(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_date_from_snippet(html, team_name):
    # Very naive regex to find dates relative to team name
    # Looking for "Feb 4" or "04/02" patterns
    snippets = re.findall(r">(.*?)</a>", html)
    
    print(f"Found {len(snippets)} snippets.")
    for s in snippets[:5]:
        print(f"- {s}")

if __name__ == "__main__":
    t = "Blackburn Rovers next match"
    print(f"Searching for: {t}")
    html = search_ddg(t)
    if html:
        extract_date_from_snippet(html, "Blackburn")
    else:
        print("Search failed.")
