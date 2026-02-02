# -*- coding: utf-8 -*-
from src.core.news_provider import NewsDataProvider
from typing import List, Dict, Any
import os
import aiohttp

class GoogleNewsProvider(NewsDataProvider):
    """
    Real implementation using NewsAPI.
    Optimized with persistent aiohttp.ClientSession.
    """
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_team_news(self, team_name: str) -> List[Dict[str, Any]]:
        if not self.api_key:
             return [{"title": "News API Key missing", "source": "System", "sentiment": "neutral"}]
             
        try:
            session = await self._get_session()
            params = {
                "q": f'{team_name} football',
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": self.api_key
            }
            async with session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    return [{"error": f"API Error {response.status}"}]
                    
                data = await response.json()
                articles = data.get("articles", [])
                
                results = []
                for art in articles:
                    results.append({
                        "title": art.get("title"),
                        "source": art.get("source", {}).get("name"),
                        "date": art.get("publishedAt")
                    })
                return results
                    
        except Exception as e:
            return [{"error": str(e)}]
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
