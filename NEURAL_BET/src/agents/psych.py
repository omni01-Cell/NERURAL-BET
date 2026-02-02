# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from src.core.news_provider import NewsDataProvider, MockNewsProvider
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

class PsychAgent(BaseAgent):
    """
    The Psychologist (Context & Motivation).
    Responsibility: Analyze the 'Human Factor' (Morale, Fatigue, Stakes).
    Input: News Headslines, Calendar Context.
    """
    
    def __init__(self, news_provider: NewsDataProvider = None):
        super().__init__(name="Freud_01", role="Psychological Profiler")
        self.llm = LLMFactory.create("psych") # Mistral Small for sentiment/text analysis
        
        if news_provider:
             self.news_provider = news_provider
        else:
             self.news_provider = MockNewsProvider()

    async def process(self, state: AgentState) -> AgentState:
        match_id = state.match_id
        # Simple parser for MVP "Home_Away"
        try:
             parts = match_id.split("_")
             home_team = parts[0]
             away_team = parts[1]
        except:
             home_team = "HomeTeam"
             away_team = "AwayTeam"
             
        # Fetch News
        home_news = await self.news_provider.get_team_news(home_team)
        away_news = await self.news_provider.get_team_news(away_team)
        
        # Construct Prompt using Professional Standards
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are "Freud_01", a specialist in Sports Psychology and Crisis Management for elite athletes.
        You read between the lines of news and interviews to detect mental fatigue, motivation gaps, and locker room tension.
        </persona>

        <news_intelligence>
        <home_team_news>
        {home_news}
        </home_team_news>
        <away_team_news>
        {away_news}
        </away_team_news>
        </news_intelligence>

        <instructions>
        Analyze the psychological high-ground for the match between {home_team} and {away_team}.
        1. **Stake Analysis**: Which team is under more survival/expectation pressure?
        2. **Momentum Check**: Is there a "Negative Spiral" in the recent news (injuries, internal conflicts)?
        3. **Locker Room Vibe**: Infer the mental freshness based on recent results and travel schedules.
        </instructions>

        <thinking>
        Consider the "Must-Win" factor vs. the "Fatigue" factor for both teams.
        </thinking>

        Final Output Format:
        **FREUD PSYCH REPORT**
        - **HOME MENTAL STATE**: (1-10) + brief description
        - **AWAY MENTAL STATE**: (1-10) + brief description
        - **PSYCH EDGE**: (Who has the mental advantage and why)
        """)

        chain = prompt | self.llm | StrOutputParser()
        
        analysis = await chain.ainvoke({
            "home_team": home_team,
            "away_team": away_team,
            "home_news": str(home_news),
            "away_news": str(away_news)
        })
        
        state.analysis_reports["psych_report"] = analysis
        return state
