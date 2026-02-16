# -*- coding: utf-8 -*-
"""
NEURAL BET: Main Pipeline Entry Point
Refactored with proper resource management and circuit breaker pattern.
"""
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
from src.providers.neural_bet_provider import NeuralBetProvider
from src.providers.google_news_provider import GoogleNewsProvider
from src.core.news_provider import MockNewsProvider
from src.core.config import validate_api_keys
from src.core.exceptions import ConfigurationError, CriticalAgentError

# Load Env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")


async def main():
    """
    Main pipeline with:
    - Fail-fast API key validation
    - Context manager for provider sessions
    - Circuit breaker on DataMiner failure
    """
    logger.info("🚀 NEURAL BET: Running Full Pipeline")
    
    # 1. Validate API keys at startup - FAIL FAST if missing
    try:
        config_status = validate_api_keys(raise_on_missing=True)
        logger.info(f"✅ API Keys validated: {', '.join(config_status['present'])}")
        if config_status['optional_missing']:
            logger.warning(f"⚠️ Optional keys missing: {', '.join(config_status['optional_missing'])}")
    except ConfigurationError as e:
        logger.error(f"❌ Configuration Error: {e}")
        raise  # Fail fast - don't silently continue
    
    # 2. Initialize State
    initial_state = AgentState(
        match_id="Arsenal_Liverpool_2026",
        analysis_reports={}
    )
    
    # 3. Use CONTEXT MANAGER for proper session cleanup
    async with NeuralBetProvider() as provider:
        
        # Setup news provider
        if os.getenv("NEWS_API_KEY"):
            news_provider = GoogleNewsProvider()
        else:
            logger.warning("⚠️ NEWS_API_KEY missing. Using Mock News.")
            news_provider = MockNewsProvider()
        
        # Instantiate Agents
        miner = DataMinerAgent(provider=provider)
        metrician = MetricianAgent()
        tactician = TacticianAgent()
        psych = PsychAgent(news_provider=news_provider)
        devil = DevilsAdvocateAgent()
        orchestrator = OrchestratorAgent()
        
        # --- PIPELINE EXECUTION ---
        logger.info("--- [PHASE 1] DATA MINING (CIRCUIT BREAKER) ---")
        
        # CIRCUIT BREAKER: If DataMiner fails, entire pipeline stops
        # DataMiner.is_critical = True, so CriticalAgentError will propagate
        try:
            state = await miner.execute(initial_state)
            logger.info("✅ DataMiner succeeded - pipeline continues")
        except CriticalAgentError as e:
            logger.error(f"🔴 CIRCUIT BREAKER TRIPPED: {e}")
            logger.error("Pipeline halted - DataMiner is critical for all downstream agents")
            raise  # Re-raise to exit cleanly
        
        logger.info("--- [PHASE 2] ANALYSIS AGENTS ---")
        
        # Step 2: Metrician (Critical)
        state = await metrician.execute(state)
        
        # Step 3: Tactician (Critical)
        state = await tactician.execute(state)
        
        # Step 4: Psych Context (Non-critical - can degrade)
        state = await psych.execute(state)
        
        # Step 5: Devil's Advocate (Non-critical - can degrade)
        state = await devil.execute(state)
        
        logger.info("--- [PHASE 3] ORCHESTRATION ---")
        
        # Step 6: Orchestrator (Critical - produces final verdict)
        state = await orchestrator.execute(state)
        
        # --- FINAL OUTPUT ---
        print("\n" + "="*50)
        print("      NEURAL BET - FINAL REPORT      ")
        print("="*50)
        
        if "orchestrator_final" in state.analysis_reports:
            print(f"\n--- 🧠 THE ORACLE VERDICT ---\n{state.analysis_reports['orchestrator_final']}")
        
        if state.errors:
            print(f"\n--- ⚠️ WARNINGS ({len(state.errors)}) ---")
            for err in state.errors:
                print(f"  • {err}")
        
        logger.info("✅ Pipeline completed successfully")
    
    # Session automatically closed by context manager


if __name__ == "__main__":
    asyncio.run(main())
