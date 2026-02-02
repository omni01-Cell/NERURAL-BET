# src/tui.py
import sys
import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
# AJOUT DE 'Center' DANS LES IMPORTS
from textual.containers import Container, Vertical, Horizontal, Center
from textual.widgets import Header, Footer, Input, Static, Label
from textual.binding import Binding

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from src.ui.widgets.dashboard_widgets import AgentSidebar, LogPanel

class NeuralBetApp(App):
    CSS_PATH = "ui/styles.tcss"
    
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
                
                # --- CORRECTION MAJEURE ICI ---
                # On utilise un conteneur 'Center' dédié qui force ses enfants
                # à se placer au milieu horizontalement.
                with Center():
                    with Vertical(classes="command-box"):
                        yield Input(placeholder="Entrez votre demande... (ex: Analyse le match Arsenal vs Liverpool)", id="startup_input")
                        yield Label("[bold blue]Engine[/] [dim]Ready[/] · [bold orange1]Waiting for input...[/]", classes="box-subtitle")

            # --- ÉCRAN 2 : DASHBOARD ---
            with Horizontal(id="dashboard_view"):
                with Container(id="sidebar-container"):
                    yield AgentSidebar()
                with Container(id="main-content-container"):
                    yield LogPanel(id="main_logs")

    def on_mount(self) -> None:
        self.query_one("#startup_input").focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        command = event.value
        if not command.strip(): return
        
        self.query_one("#startup_center").add_class("hidden")
        self.query_one("#dashboard_view").add_class("visible")
        
        log_panel = self.query_one("#main_logs")
        log_panel.write(f"[bold]Commande reçue :[/] {command}")
        log_panel.write("Initialisation du pipeline d'analyse...")

        asyncio.create_task(self.run_pipeline_simulation(log_panel))

    async def run_pipeline_simulation(self, log_panel):
        agents = ["miner", "metrician", "tactician", "xfactor", "orchestrator"]
        for agent_id in agents:
            try:
                agent_widget = self.query_one(f"#status_{agent_id}")
                agent_widget.set_active()
                log_panel.write(f"Lancement de l'agent [bold orange1]{agent_id.capitalize()}[/]...")
                await asyncio.sleep(1.0)
                log_panel.write(f"Agent [bold orange1]{agent_id.capitalize()}[/] terminé avec succès.")
                agent_widget.set_done()
                await asyncio.sleep(0.2)
            except Exception:
                pass
        log_panel.write("\n[bold green]✅ Pipeline d'analyse terminé ![/]")

if __name__ == "__main__":
    app = NeuralBetApp()
    app.run()
