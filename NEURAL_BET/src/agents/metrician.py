# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.core.schemas import MetricianOutput

class MetricianAgent(BaseAgent):
    """
    The Metrician (Analyst).
    Responsibility: Analyze raw stats (xG, PPDA, etc.) to detect luck/variance.
    """
    
    # Stats analysis is REQUIRED for valid output
    is_critical: bool = True
    
    def __init__(self):
        super().__init__(name="Metrician_Alpha", role="Data Analyst")
        # Load the specialized model (Mistral Small)
        self.llm = LLMFactory.create("metrician")

    async def process(self, state: AgentState) -> AgentState:
        # Validation guard: fail-fast if no data
        if not state.match_data:
            raise ValueError(
                "Metrician requires match_data but received None. "
                "DataMiner likely failed upstream."
            )

        parser = PydanticOutputParser(pydantic_object=MetricianOutput)

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

        <formatting>
        {format_instructions}
        </formatting>

        <thinking>
        Briefly reason step-by-step about the xG vs Goals variance before rendering your report.
        </thinking>
        """)

        # Execute Chain
        chain = prompt | self.llm | parser
        analysis = await chain.ainvoke({
            "match_data": str(state.match_data),
            "format_instructions": parser.get_format_instructions()
        })
        
        state.analysis_reports["metrician_report"] = analysis
        return state
