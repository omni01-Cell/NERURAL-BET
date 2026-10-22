# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class XFactorAgent(BaseAgent):
    """
    The X-Factor Agent (Variance Specialist).
    Responsibility: Analyze finishing efficiency (xGOT vs xG) and NPxG/Sh.
    Detects if a team is over-performing or under-performing.
    """
    
    def __init__(self):
        super().__init__(name="X-Factor_Unit", role="Variance Analyst")
        self.llm = LLMFactory.create("x_factor")

    async def process(self, state: AgentState) -> AgentState:
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "X-Factor Unit", a cold, clinical analyst obsessed with finishing efficiency.
        You look past the total xG to see the "Quality of the Shot" and the "Quality of the Finish".
        </persona>

        <context>
        Match Data: {match_data}
        Metrician Report: {metrician_report}
        </context>

        <instructions>
        Analyze the "X-Factor" for both teams:
        1. **NPxG/Sh (Non-Penalty xG per Shot)**: Is one team taking high-quality shots (>0.15) or just "farming" low-quality shots?
        2. **xGOT vs xG (Finishing quality)**: If xGOT is higher than xG, the attackers are in peak form. If much lower, they are failing in front of goal.
        3. **The 'Wall' Factor**: Analyze the goalkeeper's recent form if available (Goals Prevented).
        
        Use the 4D V2.0 Methodology.
        </instructions>

        Output Format:
        ### 🧪 Reasoning
        - Discuss NPxG/Sh trends.
        - Discuss the xGOT differential.
        
        ### 🎯 Verdict
        (Highly efficient / Stérile / Random)
        """)

        chain = prompt | self.llm | StrOutputParser()
        
        metrician_input = state.analysis_reports.get("metrician_report", "No data")
        
        analysis = await chain.ainvoke({
            "match_data": str(state.match_data), 
            "metrician_report": metrician_input
        })
        
        state.analysis_reports["xfactor_report"] = analysis
        return state
