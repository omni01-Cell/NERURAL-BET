# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class OrchestratorAgent(BaseAgent):
    """
    The Orchestrator (The Boss).
    Responsibility: Synthesize all reports (Metrician, Tactician, Devil's Advocate).
    Produce the Final Verdict & Scenario.
    Uses Gemini 1.5 Pro (Large Context).
    """
    
    # Final synthesis MUST succeed for valid output
    is_critical: bool = True
    
    def __init__(self):
        super().__init__(name="Orchestrator_X", role="Synthesis Loop")
        # Kimi k2.5 for high-level reasoning
        self.llm = LLMFactory.create("orchestrator")

    async def process(self, state: AgentState) -> AgentState:
        # Gather Intelligence
        metrician_rpt = state.analysis_reports.get("metrician_report", "N/A")
        tactician_rpt = state.analysis_reports.get("tactician_report", "N/A")
        devil_rpt = state.analysis_reports.get("devils_advocate_report", "N/A")
        
        from src.core.schemas import OrchestratorOutput
        from langchain_core.output_parsers import PydanticOutputParser

        parser = PydanticOutputParser(pydantic_object=OrchestratorOutput)

        # The Final Prompt with Synthesis Protocol
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "Grand Orchestrator", the final decision-maker of the Neural Bet System.
        Your intellect is vast, and your ability to synthesize conflicting information is unmatched.
        You weigh evidence like a judge and predict outcomes like an Oracle.
        </persona>

        <intelligence_reports>
        <stats_report>{metrician_rpt}</stats_report>
        <tactics_report>{tactician_rpt}</tactics_report>
        <critic_report>{devil_rpt}</critic_report>
        </intelligence_reports>

        <instructions>
        Your task is to reach a final, probabilistic conclusion about the match outcome.
        1. **Weigh the Evidence**: Does the tactical fit (Tactician) confirm or negate the statistical noise (Metrician)?
        2. **Assess the Threat**: Is the Devil's Advocate warning a credible 'Black Swan' or just noise?
        3. **Synthesize the Script**: Describe the most likely narrative flow of the game.
        </instructions>

        <thinking>
        Evaluate the conflict between the 3 agents. Who has the strongest case for this specific match?
        Determine the true probability of each outcome (1X2).
        </thinking>

        <formatting>
        {format_instructions}
        </formatting>
        """)

        chain = prompt | self.llm | parser
        
        analysis = await chain.ainvoke({
            "metrician_rpt": str(metrician_rpt),
            "tactician_rpt": str(tactician_rpt),
            "devil_rpt": str(devil_rpt),
            "format_instructions": parser.get_format_instructions()
        })
        
        state.analysis_reports["orchestrator_final"] = analysis
        return state
