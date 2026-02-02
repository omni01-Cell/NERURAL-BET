# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Grid, Container
from textual.widgets import Header, Footer, Button, Static, RichLog
from textual.events import Mount

from src.ui.widgets.dashboard_widgets import LogPanel, MatchInfoWidget, StatusWidget
from src.agents.base import AgentState
from src.agents.data_miner import DataMinerAgent
from src.agents.metrician import MetricianAgent
from src.agents.tactician import TacticianAgent
from src.agents.psych import PsychAgent
from src.agents.devils_advocate import DevilsAdvocateAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.market import MarketAgent
from src.agents.value_hunter import ValueHunterAgent
from src.providers.neural_bet_provider import NeuralBetProvider
from src.core.news_provider import MockNewsProvider 

# Load Env
load_dotenv()

class TuiLogHandler(logging.Handler):
    """
    Custom Logging Handler to redirect logs to Textual RichLog widget.
    """
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance

    def emit(self, record):
        log_entry = self.format(record)
        # Thread-safe callback to the app
        self.app_instance.call_from_thread(self.app_instance.log_to_panel, log_entry)

class NeuralBetApp(App):
    """
    Main Neural Bet Terminal Interface.
    """
    CSS_PATH = "ui/styles.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "run_analysis", "Run Analysis"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_layout"):
            yield MatchInfoWidget(id="match_box")
            yield StatusWidget(id="status_box")
            yield LogPanel(id="log_box")
        yield Footer()

    def on_mount(self) -> None:
        """
        Setup logging when app starts.
        """
        self.setup_logging()
        self.log_to_panel("[bold cyan]System Initialized. Press 'R' to start analysis.[/bold cyan]")

    def setup_logging(self):
        # Create bridge between standard logging and TUI
        handler = TuiLogHandler(self)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        # Attach to root logger
        root_logger = logging.getLogger()
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    def log_to_panel(self, message: str):
        try:
            self.query_one("#log_box").write_log(message)
        except:
            pass 

    async def action_run_analysis(self) -> None:
        """
        Trigger the full AI Pipeline.
        """
        # Key Check
        has_keys = os.getenv("MISTRAL_API_KEY") and os.getenv("GROQ_API_KEY") and os.getenv("FIREWORKS_API_KEY")
        if not has_keys:
            self.log_to_panel("[bold red]❌ ERROR: API KEYS MISSING.[/bold red]")
            self.log_to_panel("Please fill MISTRAL_API_KEY, GROQ_API_KEY, and FIREWORKS_API_KEY in .env")
            return

        self.log_to_panel("[bold green]🚀 Launching Neural Bet Pipeline...[/bold green]")
        # Track tasks to avoid garbage collection or orphan tasks
        if not hasattr(self, "_analysis_tasks"):
            self._analysis_tasks = set()
        
        task = asyncio.create_task(self.run_pipeline())
        self._analysis_tasks.add(task)
        task.add_done_callback(self._analysis_tasks.discard)

    async def run_pipeline(self):
        try:
            # Update Status
            self.query_one("#agent_status").update("🟡 Agents: BUSY")
            
            # 1. Setup State
            match_id = "Arsenal_Liverpool_2026"
            state = AgentState(match_id=match_id, analysis_reports={})
            
            # 2. Setup Providers
            real_provider = NeuralBetProvider()
            news_provider = MockNewsProvider() 
            
            # 3. Instantiate Agents
            logging.info("Initializing Intelligence Agents...")
            miner = DataMinerAgent(provider=real_provider)
            metrician = MetricianAgent()
            tactician = TacticianAgent()
            psych = PsychAgent(news_provider=news_provider)
            devil = DevilsAdvocateAgent()
            orchestrator = OrchestratorAgent()
            market = MarketAgent()
            hunter = ValueHunterAgent()

            # 4. Execute Pipeline (Standardized execute() call handles logging/errors)
            state = await miner.execute(state)
            state = await metrician.execute(state)
            state = await tactician.execute(state)
            state = await psych.execute(state)
            state = await devil.execute(state)
            state = await orchestrator.execute(state)
            state = await market.execute(state)
            state = await hunter.execute(state)
            
            logging.info("[bold green]✅ Analysis Sequence Complete.[/bold green]")
            
            # Update Status
            self.query_one("#agent_status").update("🟢 Agents: IDLE")
            
            # Final Results in Logs
            verdict = state.analysis_reports.get("orchestrator_final", "N/A")
            value = state.analysis_reports.get("value_report", "N/A")
            
            logging.info(f"\n[bold cyan]--- THE ORACLE VERDICT ---[/bold cyan]\n{verdict}")
            logging.info(f"\n[bold yellow]--- VALUE OPPORTUNITY ---[/bold yellow]\n{value}")

        except Exception as e:
            logging.error(f"UI Pipeline Fatal Error: {str(e)}")
            self.query_one("#agent_status").update("🔴 Agents: ERROR")

if __name__ == "__main__":
    app = NeuralBetApp()
    app.run()
