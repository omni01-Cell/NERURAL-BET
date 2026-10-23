# src/tui.py
import asyncio
import os

# Imports des Agents et Providers
from datetime import datetime

from dotenv import load_dotenv
from rich.errors import MarkupError
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, Vertical
from textual.widgets import Input, Label, Static

from src.agents.base import AgentState
from src.agents.data_miner import DataMinerAgent
from src.agents.devils_advocate import DevilsAdvocateAgent
from src.agents.metrician import MetricianAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.psych import PsychAgent
from src.agents.tactician import TacticianAgent
from src.agents.x_factor import XFactorAgent
from src.core.news_provider import MockNewsProvider
from src.providers.google_news_provider import GoogleNewsProvider

# REMOVED: MarketAgent and ValueHunterAgent (deprecated)
from src.providers.neural_bet_provider import NeuralBetProvider

load_dotenv()


class NeuralBetApp(App):
    CSS_PATH = "ui/styles.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+d", "toggle_dark", "Dark/Light"),
        ("ctrl+p", "palette", "Palette"),
    ]

    LOGO = r"""
[bold #FF8C00]███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ██╗     [/]
[bold #FF8C00]████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║     [/]
[bold #FF8C00]██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║██║     [/]
[bold #FF8C00]██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║██║     [/]
[bold #FF8C00]██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║███████╗[/]
[bold #FF8C00]╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[/]
[bold #8B4500]██████╗ ███████╗████████╗[/]
[bold #8B4500]██╔══██╗██╔════╝╚══██╔══╝[/]
[bold #8B4500]██████╔╝█████╗     ██║   [/]
[bold #8B4500]██╔══██╗██╔══╝     ██║   [/]
[bold #8B4500]██████╔╝███████╗   ██║   [/]
[bold #8B4500]╚═════╝ ╚══════╝   ╚═╝   [/]
"""

    def compose(self) -> ComposeResult:
        with Container(id="app_view"):
            # --- ÉCRAN 1 : ACCUEIL ---
            with Container(id="startup_center"):
                yield Label(self.LOGO, classes="logo-title")

                with Center():
                    with Vertical(classes="command-box"):
                        yield Input(
                            placeholder="Entrez votre demande... (ex: Analyse le match Arsenal vs Liverpool)",
                            id="startup_input",
                        )
                        yield Label(
                            "[bold blue]Engine[/] [dim]Ready[/] · [bold orange1]Waiting for input...[/]",
                            classes="box-subtitle",
                        )

            # --- ÉCRAN 2 : DASHBOARD (Chat-Based) ---
            with Container(id="dashboard_view"):
                # Header bar: titre dynamique (gauche) + NeuralBet+stats (droite)
                with Horizontal(id="header_row"):
                    yield Static(
                        "# En attente...", id="header_title"
                    )  # Titre dynamique
                    yield Static(
                        "NeuralBet  [dim]v1.0.0[/]", id="header_brand"
                    )  # Brand fixe

                # Zone de chat (pleine largeur, sans sidebar)
                with Vertical(id="chat_area"):
                    from textual.widgets import RichLog

                    yield RichLog(
                        id="chat_messages", wrap=True, highlight=True, markup=True
                    )

                    # Zone d'input avec hint "assist"
                    with Container(id="input_wrapper"):
                        yield Input(placeholder="", id="chat_input")
                        with Horizontal(id="input_hints"):
                            # Label unique dynamique, style bleu par défaut
                            yield Label("[#3a8fd9]Assist[/]", id="agent_label")

                # Footer avec vrais raccourcis
                yield Static(
                    "[bold]ctrl+q[/] quit  [bold]ctrl+d[/] theme  [dim]ctrl+p[/] palette",
                    id="footer_bar",
                )

    def on_mount(self) -> None:
        self.query_one("#startup_input").focus()
        self._pending_match = None  # Store pending match for confirmation

    def _update_agent_label(self, agent_name: str) -> None:
        """Update the agent label in the input area."""
        self.query_one("#agent_label").update(f"[#3a8fd9]{agent_name}[/]")

    def _user_msg(self, text: str) -> None:
        """Display a user message with cyan left border and dark background."""
        from rich.text import Text

        chat = self.query_one("#chat_messages")

        # Spacer au début pour séparer du message précédent
        spacer = Text("\n")

        # Créer le texte avec un style de fond
        msg = Text(text, style="white on #262626")

        # Ajouter la bordure cyan
        border = Text("│ ", style="#3a8fd9 bold on #262626")

        # Combiner
        full_msg = spacer + border + msg

        chat.write(full_msg)

    def _bot_msg(self, text: str) -> None:
        """Display a bot message (no border, slightly indented, with background)."""
        from rich.markup import render
        from rich.text import Text

        chat = self.query_one("#chat_messages")

        # Style de fond pour le bot (légèrement différent ou identique)
        bot_style = "on #1e1e1e"  # Un peu plus sombre que l'user, ou pareil

        # Spacer pour séparer de la question précédente
        spacer = Text("\n")

        # Parse Rich markup in text
        try:
            rendered = render(text)
            # Appliquer le style de fond au rendu si possible, ou envelopper
            # Pour Rich markup, le style appliqué au Text conteneur devrait marcher
            msg = Text("  ", style=bot_style)
            msg.append(rendered)
            # On force le style de fond sur tout le texte ajouté
            msg.stylize(bot_style)

            chat.write(spacer + msg)
        except (MarkupError, ValueError, TypeError, IndexError):
            chat.write(spacer + Text(f"  {text}", style=bot_style))

    def _log(self, msg: str) -> None:
        """Write a timestamped log message (for debug/internal)."""
        chat = self.query_one("#chat_messages")
        ts = datetime.now().strftime("%H:%M:%S")
        chat.write(f"[dim]{ts}[/]  {msg}")

    async def _generate_title(self, user_query: str) -> str:
        """Generate a short match title using Groq LLM (ultra fast)."""
        from src.core.llm import LLMFactory

        try:
            llm = LLMFactory.get_groq_model("llama-3.1-8b-instant", temperature=0.0)

            prompt = f"""Extract the match title from this query. Return ONLY the match name in format "Team1 vs Team2".
No explanation, no extra text, just the match name.

Query: {user_query}
Match:"""

            response = await llm.ainvoke(prompt)
            title = response.content.strip()

            # Clean up common issues
            title = title.replace('"', "").replace("'", "")
            if len(title) > 50:  # Fallback if too long
                title = title[:50] + "..."

            return title
        except Exception:
            # Fallback: extract from query directly
            return user_query[:40] if len(user_query) > 40 else user_query

    def _update_header(self, match_name: str) -> None:
        """Update header title with match name."""
        self.query_one("#header_title").update(f"# {match_name}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Handle startup input
        if event.input.id == "startup_input":
            command = event.value
            if not command.strip():
                return

            # Transition UI
            self.query_one("#startup_center").add_class("hidden")
            self.query_one("#dashboard_view").add_class("visible")

            # Display user message
            self._user_msg(command)

            # Generate dynamic title for header (non-blocking)
            title = await self._generate_title(command)
            self._update_header(title)

            # Focus chat input for next messages
            self.query_one("#chat_input").focus()

            # Process the command
            await self._process_command(command)

        # Handle chat input (continued conversation)
        elif event.input.id == "chat_input":
            user_input = event.value
            event.input.value = ""  # Clear input
            if not user_input.strip():
                return

            self._user_msg(user_input)

            # Check if we're waiting for match confirmation
            if self._pending_match:
                await self._handle_confirmation(user_input)
            else:
                # New query in conversation
                await self._process_command(user_input)

    async def _process_command(self, command: str) -> None:
        """Process a user command (analyze request)."""
        from src.agents.dispatcher import DispatcherAgent

        dispatcher = DispatcherAgent()

        try:
            dispatch_result = await dispatcher.run(command)

            if not dispatch_result.match_found:
                self._bot_msg(
                    f"Je n'ai pas trouvé ce match. {dispatch_result.reasoning}"
                )
                self._bot_msg(
                    "Essayez avec plus de précision, ex: [bold]Arsenal vs Chelsea Premier League[/]"
                )
                return

            # Store pending match and ask for confirmation
            self._pending_match = dispatch_result

            # Format date nicely
            date_str = dispatch_result.date if dispatch_result.date else "date inconnue"

            # Conversational response
            self._bot_msg(
                f"salut est-ce bien le match [bold]{dispatch_result.home} vs {dispatch_result.away}[/] - "
                f"{dispatch_result.league or 'League'} pour le {date_str} que vous voulez analyser ?"
            )

        except Exception as e:
            self._bot_msg(f"Désolé, une erreur s'est produite : {e}")

    async def _handle_confirmation(self, user_input: str) -> None:
        """Handle user confirmation of pending match."""
        lower = user_input.lower().strip()

        if lower in (
            "oui",
            "yes",
            "y",
            "o",
            "ok",
            "c'est ça",
            "correct",
            "exactement",
            "go",
            "lance",
        ):
            match = self._pending_match
            self._pending_match = None

            self._update_header(f"{match.home} vs {match.away}")
            self._bot_msg(
                f"Parfait ! Je lance l'analyse de [bold]{match.home} vs {match.away}[/]..."
            )

            # Launch pipeline
            asyncio.create_task(self.run_real_pipeline(match.match_id))

        elif lower in ("non", "no", "n", "pas ça", "autre"):
            self._pending_match = None
            self._bot_msg("D'accord, quel match souhaitez-vous analyser ?")
        else:
            # Treat as new query
            self._pending_match = None
            await self._process_command(user_input)

    async def run_real_pipeline(self, match_id):
        """Exécute le pipeline complet avec graphe asynchrone."""

        # 1. Verification des clés API
        has_keys = (
            os.getenv("MISTRAL_API_KEY")
            and os.getenv("GROQ_API_KEY")
            and os.getenv("FIREWORKS_API_KEY")
        )
        if not has_keys:
            self._bot_msg(
                "⚠️ [bold red]Clés API manquantes[/] - Vérifiez votre fichier .env"
            )
            return

        # 2. Instantiation
        try:
            if os.getenv("NEWS_API_KEY"):
                news_provider = GoogleNewsProvider()
            else:
                news_provider = MockNewsProvider()

            # Initial State
            state = AgentState(match_id=match_id, analysis_reports={})

            # --- Instanciation des Agents ---
            real_provider = NeuralBetProvider()
            miner = DataMinerAgent(provider=real_provider)
            metrician = MetricianAgent()
            tactician = TacticianAgent()
            psych = PsychAgent(news_provider=news_provider)
            xfactor = XFactorAgent()
            devil = DevilsAdvocateAgent()
            orchestrator = OrchestratorAgent()

        except Exception as e:
            self._bot_msg(f"Erreur d'initialisation: {e}")
            return

        # 3. Execution Loop
        self._bot_msg("🔍 Je collecte les données du match...")

        # --- ÉTAPE 1 : Data Mining ---
        try:
            self._update_agent_label("Data Miner")
            state = await miner.execute(state)
            self._bot_msg("✅ Données collectées")
        except Exception as e:
            self._bot_msg(f"❌ Erreur de collecte: {e}")
            self._update_agent_label("Assist")
            return

        # --- ÉTAPE 2 : Analyse Parallèle ---
        self._bot_msg("🧠 Analyse en cours par nos experts...")
        self._update_agent_label("The Swarm")

        try:

            async def run_agent_safe(agent, base_state: AgentState, report_key: str):
                isolated_state = AgentState(
                    match_id=base_state.match_id,
                    match_data=base_state.match_data,
                    market_data=base_state.market_data,
                    analysis_reports={},
                    errors=[],
                )
                result_state = await agent.execute(isolated_state)
                return result_state

            results = await asyncio.gather(
                run_agent_safe(metrician, state, "metrician_report"),
                run_agent_safe(tactician, state, "tactician_report"),
                run_agent_safe(psych, state, "psych_report"),
                run_agent_safe(xfactor, state, "xfactor_report"),
                return_exceptions=True,
            )

            for result in results:
                if isinstance(result, Exception):
                    state.errors.append(str(result))
                elif isinstance(result, AgentState):
                    state.analysis_reports.update(result.analysis_reports)
                    state.errors.extend(result.errors)

        except Exception as e:
            self._bot_msg(f"⚠️ Erreur durant l'analyse parallèle: {e}")

        # --- ÉTAPE 3 : Devil's Advocate ---
        try:
            self._update_agent_label("Devil's Advocate")
            state = await devil.execute(state)
        except Exception as e:
            self._bot_msg(f"⚠️ Devil's Advocate: {e}")

        # --- ÉTAPE 4 : Orchestrator ---
        try:
            self._bot_msg("📊 Synthèse du verdict en cours...")
            self._update_agent_label("Orchestrator")
            state = await orchestrator.execute(state)
        except Exception as e:
            self._bot_msg(f"⚠️ Orchestrator: {e}")

        # --- Affichage Final ---
        if "orchestrator_final" in state.analysis_reports:
            orch_out = state.analysis_reports["orchestrator_final"]
            try:
                self._bot_msg("\\n[bold]═══ VERDICT NEURAL BET ═══[/]")
                self._bot_msg(f"🏆 [bold]Prédiction:[/] {orch_out.winner_prediction}")
                self._bot_msg(
                    f"📊 [bold]Confiance:[/] {orch_out.confidence_score * 100:.1f}%"
                )
                self._bot_msg(
                    f"🔑 [bold]Facteur décisif:[/] {orch_out.decisive_factor}"
                )
                self._bot_msg(f"📜 [bold]Raisonnement:[/] {orch_out.logic_summary}")
            except (AttributeError, TypeError, ValueError):
                self._bot_msg(str(orch_out))

        self._bot_msg("\\n✨ [bold green]Analyse terminée ![/] Une autre question ?")
        self._update_agent_label("Assist")


if __name__ == "__main__":
    app = NeuralBetApp()
    app.run()
