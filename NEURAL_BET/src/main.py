# -*- coding: utf-8 -*-
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Ensure root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.base import AgentState
from src.agents.data_miner import DataMinerAgent
from src.agents.metrician import MetricianAgent
from src.agents.tactician import TacticianAgent
from src.agents.devils_advocate import DevilsAdvocateAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.psych import PsychAgent
from src.agents.market import MarketAgent
from src.agents.value_hunter import ValueHunterAgent
from src.providers.neural_bet_provider import NeuralBetProvider
from src.providers.google_news_provider import GoogleNewsProvider
from src.core.news_provider import MockNewsProvider

# Load Env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

async def main():
    logger.info("🚀 NEURAL BET: Running Full Pipeline (Double Blind Mode)")
    
    # 1. Initialize State
    initial_state = AgentState(
        match_id="Arsenal_Liverpool_2026",
        analysis_reports={}
    )
    
    # 2. Instantiate Components
    real_provider = NeuralBetProvider()
    
    if os.getenv("NEWS_API_KEY"):
        news_provider = GoogleNewsProvider()
    else:
        logger.warning("⚠️ NEWS_API_KEY missing. Using Mock News.")
        news_provider = MockNewsProvider()
    
    # Branch A: Analysis
    miner = DataMinerAgent(provider=real_provider)
    metrician = MetricianAgent()
    tactician = TacticianAgent()
    psych = PsychAgent(news_provider=news_provider)
    devil = DevilsAdvocateAgent()
    orchestrator = OrchestratorAgent()
    
    # Branch B: Market
    market = MarketAgent() # Uses Mock by default for now
    
    # Convergence
    hunter = ValueHunterAgent()
    
    # --- PIPELINE SEQUENCE ---
    # In a real async graph, Branch A and B would run concurrently.
    
    logger.info("--- [BRANCH A] STARTING SPORT ANALYSIS ---")
    # Step 1: Data Mining (Real)
    state = await miner.execute(initial_state)
    
    has_keys = os.getenv("MISTRAL_API_KEY") and os.getenv("GROQ_API_KEY") and os.getenv("FIREWORKS_API_KEY")
    if not has_keys:
         logger.warning("⚠️  API Keys missing (MISTRAL, GROQ, FIREWORKS). Cannot run LLM Agents.")
         return

    # Step 2: Metrician
    state = await metrician.execute(state)
    
    # Step 3: Tactician
    state = await tactician.execute(state)
    
    # Step 4: Psych Context
    state = await psych.execute(state)
    
    # Step 5: Devil's Advocate
    state = await devil.execute(state)
    
    # Step 6: Orchestrator (Produces Verdict)
    state = await orchestrator.execute(state)
    logger.info("--- [BRANCH A] ANALYSIS COMPLETE ---")
    
    logger.info("--- [BRANCH B] STARTING MARKET SCAN ---")
    # Step 7: Market (Ideally runs parallel to A)
    state = await market.execute(state)
    
    logger.info("--- [CONVERGENCE] HUNTING VALUE ---")
    # Step 8: Value Hunter
    state = await hunter.execute(state)
    
    # Final Output
    print("\n" + "="*50)
    print("      NEURAL BET - FINAL REPORT      ")
    print("="*50)
    
    if "orchestrator_final" in state.analysis_reports:
        print(f"\n--- 🧠 THE ORACLE VERDICT ---\n{state.analysis_reports['orchestrator_final']}")
    
    if "value_report" in state.analysis_reports:
        print(f"\n--- 💰 VALUE HUNTER STRATEGY ---\n{state.analysis_reports['value_report']}")
    else:
        print("\n(No value report generated)")

if __name__ == "__main__":
    asyncio.run(main())
