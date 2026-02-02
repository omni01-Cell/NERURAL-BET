from textual.widgets import Static, RichLog
from textual.app import ComposeResult
from datetime import datetime

class LogPanel(Static):
    """
    Scrolling Log Panel to display agent thoughts.
    """
    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="log_stream")

    def write_log(self, message: str):
        log_widget = self.query_one(RichLog)
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_widget.write(f"[{timestamp}] {message}")

class MatchInfoWidget(Static):
    """
    Displays current match details.
    """
    def compose(self) -> ComposeResult:
        yield Static("⚽ MATCH: Waiting for selection...", id="match_title", classes="box-title")
        yield Static("\n Analyzing: [bold]Arsenal vs Liverpool[/bold]\n League: Premier League", id="match_details")

class StatusWidget(Static):
    """
    Displays System Status and Spinner.
    """
    def compose(self) -> ComposeResult:
        yield Static("SYSTEM STATUS", classes="box-title")
        yield Static("🟢 Agents: IDLE", id="agent_status")
        yield Static("💸 Market: CONNECTED", id="market_status")
