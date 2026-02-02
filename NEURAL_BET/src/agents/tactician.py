# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

class TacticianAgent(BaseAgent):
    """
    The Tactician (Strategist).
    Responsibility: Analyze stylistic matchups (e.g., High Line vs Counter Attack).
    Uses valid Reasoner models via Gemini Pro.
    """
    
    def __init__(self):
        super().__init__(name="Tactician_Prime", role="Tactical Analyst")
        # Mistral Large for tactical depth
        self.llm = LLMFactory.create("tactician")

    async def process(self, state: AgentState) -> AgentState:
        # Dependency Check (Warning only, doesn't stop logic)
        if "metrician_report" not in state.analysis_reports:
             self.log("Metrician report missing, proceeding with raw data.", level="warning")
        
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "Tactician Prime", a master football strategist and former elite manager.
        You specialize in system matchups, pressing triggers, and transition patterns.
        </persona>

        <context>
        Metrician's Statistical Note: {metrician_report}
        </context>

        <instructions>
        Your task is to analyze the "Tactical Fit" between the two opponents.
        1. Identify the core tactical identity of both teams.
        2. Find the "Tactical Mismatch": Does Home's strength exploit Away's specific weakness?
        3. Evaluate if the Metrician's statistical findings are explained by tactical systems (e.g., low xG due to low-block).
        
        Avoid generic statements. Be specific about tactical systems (e.g. 4-3-3 Gegenpress vs 5-4-1 Low Block).
        </instructions>

        <match_data>
        {match_data}
        </match_data>

        Final Output Format:
        **TACTICAL BREAKDOWN**
        - **BATTLE OF SYSTEMS**: (Short description)
        - **THE EXPLOIT**: (The specific tactical hole one team will use)
        - **VERDICT**: (Tactical advantage: Home / Away / Neutral)
        """)

        chain = prompt | self.llm | StrOutputParser()
        
        # We pass empty string if metrician report is missing to avoid crash
        metrician_input = state.analysis_reports.get("metrician_report", "No data")
        
        analysis = await chain.ainvoke({
            "match_data": str(state.match_data), 
            "metrician_report": metrician_input
        })
        
        state.analysis_reports["tactician_report"] = analysis
        return state
