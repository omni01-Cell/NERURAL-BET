# src/ui/widgets/dashboard_widgets.py
from textual.widgets import Static, RichLog, Label
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from datetime import datetime

class ActivityIndicator(Static):
    """Petit indicateur animé (⠋⠙⠹...)."""
    def on_mount(self) -> None:
        self.step = 0
        self.interval = None
    
    def start(self):
        if not self.interval:
            self.interval = self.set_interval(0.15, self.animate)
    
    def stop(self):
        if self.interval:
            self.interval.stop()
            self.interval = None
            self.update("") # Efface l'animation

    def animate(self):
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.update(f"[bold orange1]{chars[self.step % len(chars)]}[/]")
        self.step += 1

class AgentStatusItem(Static):
    """Un bloc représentant un agent dans la sidebar."""
    def __init__(self, label: str, id: str):
        super().__init__(id=id)
        self.label_text = label

    def compose(self) -> ComposeResult:
        yield Label(self.label_text, classes="agent-name")
        yield ActivityIndicator(id=f"{self.id}-spinner")
        yield Label("", id=f"{self.id}-icon") # Pour le check vert à la fin

    def set_active(self):
        self.add_class("active")
        self.remove_class("done")
        self.query_one(ActivityIndicator).start()
        self.query_one(f"#{self.id}-icon").update("")

    def set_done(self):
        self.remove_class("active")
        self.add_class("done")
        self.query_one(ActivityIndicator).stop()
        self.query_one(f"#{self.id}-icon").update("[bold]✔[/]")

class AgentSidebar(Container):
    """Le contenu de la colonne de gauche (largeur 25)."""
    def compose(self) -> ComposeResult:
        yield Label("AGENTS DU PIPELINE", classes="sidebar-title")
        # Liste des agents
        yield AgentStatusItem("1. Data Miner", id="status_miner")
        yield AgentStatusItem("2. Metrician", id="status_metrician")
        yield AgentStatusItem("3. Tactician", id="status_tactician")
        yield AgentStatusItem("4. Psych Agent", id="status_psych")
        yield AgentStatusItem("5. X-Factor", id="status_xfactor")
        yield AgentStatusItem("6. Market Agent", id="status_market")
        yield AgentStatusItem("7. Devil's Advocate", id="status_devil")
        yield AgentStatusItem("8. Orchestrator", id="status_orchestrator")
        yield AgentStatusItem("9. Value Hunter", id="status_value_hunter")
        
        # Placeholder pour ton "autre graphique"
        yield Label("\n[STATISTIQUES]", classes="sidebar-title")
        yield Static("[dim]Graphique de confiance\nen attente de données...[/]", classes="graph-placeholder")

class LogPanel(Static):
    """Le panneau principal de droite pour les logs."""
    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="main_log", wrap=True)

    def write(self, message: str):
        log_widget = self.query_one(RichLog)
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Ajoute l'heure en gris avant le message
        log_widget.write(f"[dim]{timestamp}[/dim]  {message}")
