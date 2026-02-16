# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ValueHunterAgent(BaseAgent):
    """
    The Value Hunter (Convergence Point).
    Responsibility: Compare Orchestrator's Verdict vs Market Odds.
    Identify POSITIVE EXPECTED VALUE (EV+) Bets.
    """
    
    def __init__(self):
        super().__init__(name="Hunter_01", role="Financial Strategist")
        # Groq Compound for cold math/logic
        self.llm = LLMFactory.create("value_hunter") 

    async def process(self, state: AgentState) -> AgentState:
        if not state.market_data:
            self.log("Skipping Value Hunt - No market data available.", level="warning")
            return state
            
        orchestrator_output = state.analysis_reports.get("orchestrator_final")
        
        # Check if Orchestrator failed or returned string (e.g. error)
        if not orchestrator_output or not hasattr(orchestrator_output, "confidence_score"):
             self.log("Orchestrator output missing or invalid (not an object).", level="error")
             return state

        market_odds = state.market_data
        
        # --- Python Math Logic ---
        confidence = orchestrator_output.confidence_score # float 0.0-1.0
        prediction = orchestrator_output.winner_prediction # HOME, DRAW, AWAY
        
        # Map prediction to odd key
        odd_key_map = {
            "HOME": "home_win",
            "DRAW": "draw",
            "AWAY": "away_win"
        }
        
        target_odd_key = odd_key_map.get(prediction)
        target_odd = market_odds.get(target_odd_key, 1.0)
        
        # EV Computation: (Probability * Odd) - 1
        # Probability is our confidence
        ev_value = (confidence * target_odd) - 1.0
        
        # --- LLM Reasoning Portion ---
        from src.core.schemas import ValueHunterOutput
        from langchain_core.output_parsers import PydanticOutputParser
        
        parser = PydanticOutputParser(pydantic_object=ValueHunterOutput)
        
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "Value Hunter", a elite financial strategist specialized in sports arbitrage and inefficiency detection.
        You treat football matches as stock options. You have no emotions, only Expected Value (EV).
        </persona>

        <inputs>
        <verdict_narrative>{narrative}</verdict_narrative>
        <target_bet>{prediction}</target_bet>
        <market_odd>{odd}</market_odd>
        <calculated_ev>{ev}</calculated_ev>
        </inputs>

        <instructions>
        Your goal is to write the strategic justification for this bet.
        1. **Analyze the Edge**: We calculated an EV of {ev_formatted}. Explain why this is good (or bad).
        2. **Risk Assessment**: If EV > 0.05 (5%), recommend a BUY. If EV < 0, recommend NO BET.
        3. **Stake Sizing**: Suggest a stake (1-10 units) proportional to the edge (Kelly Criterion logic).
        
        Note: The EV has ALREADY been calculated. Do not re-calculate it. Trust the input.
        </instructions>

        <formatting>
        {format_instructions}
        </formatting>
        """)

        chain = prompt | self.llm | parser
        
        report = await chain.ainvoke({
            "narrative": orchestrator_output.logic_summary,
            "prediction": prediction,
            "odd": target_odd,
            "ev": ev_value,
            "ev_formatted": f"{ev_value*100:.2f}%",
            "format_instructions": parser.get_format_instructions()
        })
        
        # Override the EV in the report with our precise python float to ensure accuracy
        report.ev_percentage = ev_value
        
        state.analysis_reports["value_report"] = report
        return state
