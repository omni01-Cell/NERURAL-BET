# -*- coding: utf-8 -*-
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.base import AgentState, BaseAgent
from src.core.llm import LLMFactory
from src.core.schemas import DispatcherOutput
from src.providers.neural_bet_provider import NeuralBetProvider


class DispatcherAgent(BaseAgent):
    """
    Agent 0: The Dispatcher (Refactored).
    Strict 3-Step Process:
    1. EXTRACT: LLM extracts entity names (JSON only).
    2. VERIFY: Python Provider validates match/date.
    3. OUTPUT: Return standard DispatcherOutput.
    """

    def __init__(self):
        super().__init__(name="Dispatcher_00", role="Traffic Control")
        # Fast Model (Llama 8b Instant)
        self.llm = LLMFactory.create("dispatcher")
        self.provider = NeuralBetProvider()
        self.feedback_callback = None

    def set_feedback_callback(self, callback):
        """Allow TUI to hook in for streaming logs."""
        self.feedback_callback = callback

    async def _think(self, message: str):
        """Send feedback to TUI if callback exists."""
        if self.feedback_callback:
            await self.feedback_callback(message)

    def _clean_json(self, text: str) -> str:
        """Remove markdown code blocks and whitespace."""
        text = text.strip()
        # Remove ```json ... ``` or ```python ... ``` wrappers
        text = re.sub(r"^```(\w+)?\n", "", text)
        text = re.sub(r"\n```$", "", text)

        # Robust extraction: Find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return text[start : end + 1]

        return text.strip()

    async def run(self, user_input: str) -> DispatcherOutput:
        from datetime import datetime

        current_date_str = datetime.now().strftime("%Y-%m-%d")

        # Step 1: Extraction (LLM)
        await self._think(f"📅 Date système : {current_date_str}")
        await self._think("🧠 Analyse sémantique (Nettoyage entités)...")

        system_prompt = f"""You are an ENTITY EXTRACTOR for football matches.
        Current Date: {current_date_str}
        
        Task: Extract TEAM NAMES and EXPLICIT DATE HINTS from the user request.
        
        Rules:
        1. Normalize team names (e.g. "Barça" -> "FC Barcelona").
        2. Detect if a specific date or relative date (today, tomorrow, next week) is mentioned.
        3. Convert relative dates to YYYY-MM-DD if possible, otherwise keep as keyword.
        4. DO NOT GUESS a date if none is mentioned. Leave date_hint null.
        
        OUTPUT FORMAT (Strict JSON):
        {{
            "team1": "Name",
            "team2": "Name" (or null),
            "date_hint": "YYYY-MM-DD" (or null)
        }}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            raw_content = response.content
            cleaned_json = self._clean_json(raw_content)

            entities = json.loads(cleaned_json)
            t1 = entities.get("team1")
            t2 = entities.get("team2")
            d_hint = entities.get("date_hint")

            await self._think(
                f"🔍 Entités brutes : {t1} | {t2 or 'Any'} | Date: {d_hint or 'None'}"
            )

        except Exception as e:
            # Try to log the raw content if available, else generic error
            raw_preview = locals().get("raw_content", "No content")[:200]
            await self._think(f"⚠️ Erreur JSON LLM. Raw Output: {raw_preview}")

            return DispatcherOutput(
                match_found=False, reasoning=f"LLM Parsing Failed: {str(e)}"
            )

        # Step 2: Verification (Python Provider) with TIMEOUT
        # This prevents UI freeze if provider is slow/blocked
        await self._think(f"🌍 Interrogation Provider pour {t1}...")

        import asyncio

        PROVIDER_TIMEOUT_SECONDS = 15  # Max wait for provider response

        try:
            # Pass all extracted info to the provider
            # The provider decides if it trusts the date_hint or fails
            match_data = await asyncio.wait_for(
                self.provider.find_next_match(
                    team_name=t1, opponent_name=t2, date_hint=d_hint
                ),
                timeout=PROVIDER_TIMEOUT_SECONDS,
            )

            if not match_data.get("found"):
                reason = match_data.get("reason", "Match not found.")
                await self._think(f"❌ échec Provider : {reason}")
                return DispatcherOutput(match_found=False, reasoning=reason)

            # Step 3: Success
            src = match_data.get("source", "Unknown")
            await self._think(
                f"✅ Match confirmé : {match_data['home']} vs {match_data['away']} ({match_data['date']})"
            )
            await self._think(f"ℹ️ Source : {src}")

            return DispatcherOutput(
                match_found=True,
                match_id=match_data["match_id"],
                home=match_data["home"],
                away=match_data["away"],
                date=match_data["date"],
                competition=match_data["league"],
                reasoning=f"Validated via {src}",
            )

        except asyncio.TimeoutError:
            await self._think(f"⏱️ Provider timeout après {PROVIDER_TIMEOUT_SECONDS}s")
            return DispatcherOutput(
                match_found=False,
                reasoning=f"Provider verification timed out after {PROVIDER_TIMEOUT_SECONDS}s. Try again or specify a date.",
            )

        except Exception as e:
            return DispatcherOutput(
                match_found=False, reasoning=f"Provider Verification Error: {str(e)}"
            )

    async def process(self, state: AgentState) -> AgentState:
        return state
