# -*- coding: utf-8 -*-
from src.agents.base import BaseAgent, AgentState
from src.core.llm import LLMFactory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

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
            
        orchestrator_verdict = state.analysis_reports.get("orchestrator_final", "N/A")
        market_odds = state.market_data
        
        prompt = ChatPromptTemplate.from_template("""
        <persona>
        You are the "Value Hunter", a elite financial strategist specialized in sports arbitrage and inefficiency detection.
        You treat football matches as stock options. You have no emotions, only Expected Value (EV).
        </persona>

        <inputs>
        <verdict>{verdict}</verdict>
        <market_odds>{odds}</market_odds>
        </inputs>

        <instructions>
        Your goal is to find "Math Value" (Inefficiency) between our Oracle and the Bookmakers.
        1. **Probability Translation**: Convert the Oracle's narrative into a percentage probability for the primary outcome.
        2. **Value Formula**: Calculate Value % = (Our_Prob_Decimal * Market_Odd) - 1.
        3. **Risk/Reward**: Determine if the value is high enough (>5%) to justify a "BUY" (Bet).
        </instructions>

        <thinking>
        Perform the division and multiplication step-by-step. Compare 1/Odd (Market Prob) with Our Prob.
        </thinking>

        Final Output Format:
        **💰 VALUE STRATEGY REPORT**
        - **RECOMMENDED BET**: [Selection] @ [Odd]
        - **EXPECTED VALUE (EV)**: [X.XX%]
        - **EDGE OVER MARKET**: [Explain why the Oracle is smarter than the market here]
        - **STAKE ADVICE**: [Safe / Aggressive / NO BET]
        """)

        chain = prompt | self.llm | StrOutputParser()
        
        report = await chain.ainvoke({
            "verdict": orchestrator_verdict,
            "odds": str(market_odds)
        })
        
        state.analysis_reports["value_report"] = report
        return state
