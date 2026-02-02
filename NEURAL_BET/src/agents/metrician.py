# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

class MetricianAgent(BaseAgent):
    """
    The Metrician (Analyst).
    Responsibility: Analyze raw stats (xG, PPDA, etc.) to detect luck/variance.
    """
    
    def __init__(self):
        super().__init__(name="Metrician_Alpha", role="Data Analyst")
        # Load the specialized model (Mistral Small)
        self.llm = LLMFactory.create("metrician")

    async def process(self, state: AgentState) -> AgentState:
        if not state.match_data:
            state.errors.append("Metrician: No match data found to analyze.")
            return state

        # Create the prompt using Anthropic Best Practices
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "Metrician", a world-class football data scientist specialized in variance analysis and expected metrics (xG, xA, PPDA).
        Your tone is technical, objective, and clinical.
        </persona>

        <instructions>
        Your goal is to detect "LUCK" or "VARIANACE" in the recent performance of the teams.
        1. Analyze the difference between Expected Goals (xG) and Actual Goals.
        2. Identify if a team is unsustainably over-performing or under-performing.
        3. Determine if the current league position is a reflection of skill or statistical noise.
        
        STRICT CONSTRAINT: Do not be conversational. 
        If data is missing or insufficient, state "INSUFFICIENT_DATA".
        </instructions>

        <match_data>
        {match_data}
        </match_data>

        <thinking>
        Briefly reason step-by-step about the xG vs Goals variance before rendering your report.
        </thinking>

        Final Output Format:
        **TECHNICAL METRIC REPORT**
        - **VARIANCE STATE**: [CRITICAL OVERPERFORMANCE / STABLE / REGRESSION LIKELY]
        - **LUCK FACTOR**: (Brief explanation)
        - **DATA VERDICT**: (Max 50 words)
        """)

        # Execute Chain
        chain = prompt | self.llm | StrOutputParser()
        analysis = await chain.ainvoke({"match_data": str(state.match_data)})
        
        state.analysis_reports["metrician_report"] = analysis
        return state
