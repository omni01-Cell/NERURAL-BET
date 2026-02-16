# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class DevilsAdvocateAgent(BaseAgent):
    """
    The Devil's Advocate (Red Teamer).
    Responsibility: Destroy the consensus. Find the 'Black Swan'.
    Uses DeepSeek/Llama 70b via Groq.
    """
    
    # Enrichment agent: nice-to-have but not required for output
    is_critical: bool = False
    
    def __init__(self):
        super().__init__(name="Mephisto_01", role="System Critic")
        # Groq Compound for cold logic
        self.llm = LLMFactory.create("devils_advocate")

    async def process(self, state: AgentState) -> AgentState:
        # We need the previous analyses to criticize them
        metrician_report = state.analysis_reports.get("metrician_report", "No Data")
        tactician_report = state.analysis_reports.get("tactician_report", "No Data")
        
        # The System Prompt with Ruin Protocol
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are "Mephisto", the Agent of Chaos. Your sole purpose is to DESTROY the consensus.
        You are a master of identifying "Black Swans" and statistical regressions. 
        You have no bias and you enjoy being right when everyone else is wrong.
        </persona>

        <intelligence_pool>
        <match_data>{match_data}</match_data>
        <metrician_report>{metrician_report}</metrician_report>
        <tactician_report>{tactician_report}</tactician_report>
        </intelligence_pool>

        <instructions>
        Your mission: Build the strongest possible case for the UPSET or the FAILURE of the favorite.
        1. **Systemic Fatigue**: Find evidence of over-use of key players.
        2. **Tactical hubris**: Is the favorite too arrogant? (e.g. playing too high against a fast counter-attacker).
        3. **Statistical Gravity**: If the Metrician found over-performance, explain why it MUST crash today.
        
        BE BRUTAL. IF THE CONSENSUS IS "HOME WIN", YOUR JOB IS TO FIND WHY it will be an "AWAY WIN" or "DRAW".
        </instructions>

        <thinking>
        Identify the one single point of failure (The Linchpin) in the favorite's setup.
        </thinking>

        Final Output Format:
        **🔥 DESTRUCTION REPORT (MEPHISTO)**
        - **DANGER LEVEL**: [LOW / MEDIUM / CRITICAL]
        - **THE CRACK**: (The specific reason they fail)
        - **SCENARIO OF RUIN**: (How exactly it goes wrong)
        - **CONTRARIAN VERDICT**: [Why you shouldn't trust the consensus]
        """)

        chain = prompt | self.llm | StrOutputParser()
        
        analysis = await chain.ainvoke({
            "match_data": str(state.match_data),
            "metrician_report": metrician_report,
            "tactician_report": tactician_report
        })
        
        state.analysis_reports["devils_advocate_report"] = analysis
        return state
