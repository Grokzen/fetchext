from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Grid
from textual.widgets import Header, Footer, Input, DataTable, RadioSet, RadioButton, Label, TabbedContent, TabPane, Static, Markdown, Button
from textual.screen import ModalScreen
from fetchext.core import search_extension, download_extension, get_repo_stats
from fetchext.history import HistoryManager
import logging
from pathlib import Path

class ConfirmationScreen(ModalScreen[bool]):
    """Screen for confirming an action."""

    CSS = """
    ConfirmationScreen {
        align: center middle;
    }

    #dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }

    #question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }

    Button {
        width: 100%;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message, id="question"),
            Button("Yes", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

class Dashboard(Static):
    """Dashboard widget showing repository statistics."""

    def compose(self) -> ComposeResult:
        yield Label("Repository Statistics", classes="header")
        yield Container(id="stats_container")
        yield Label("Recent Activity", classes="header")
        yield DataTable(id="history_table")

    def on_mount(self) -> None:
        self.load_data()

    @work(thread=True)
    def load_data(self) -> None:
        # Load Stats
        try:
            stats = get_repo_stats(Path("."))
            self.app.call_from_thread(self.update_stats, stats)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Failed to load stats: {e}", severity="error")

        # Load History
        try:
            history = HistoryManager().get_entries(limit=10)
            self.app.call_from_thread(self.update_history, history)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Failed to load history: {e}", severity="error")

    def update_stats(self, stats) -> None:
        container = self.query_one("#stats_container")
        container.remove_children()
        
        # Create summary cards
        total_size_mb = stats.total_size_bytes / (1024 * 1024)
        
        summary = f"""
        **Total Extensions:** {stats.total_extensions}
        **Total Size:** {total_size_mb:.2f} MB
        **MV3 Extensions:** {stats.mv3_count} ({stats.mv3_count / stats.total_extensions * 100 if stats.total_extensions else 0:.1f}%)
        """
        container.mount(Markdown(summary))
        
        # Risk Distribution
        risk_md = "**Risk Distribution:**\n\n"
        for level, count in stats.risk_distribution.items():
            risk_md += f"- **{level}:** {count}\n"
        container.mount(Markdown(risk_md))

    def update_history(self, entries) -> None:
        table = self.query_one("#history_table", DataTable)
        table.clear()
        table.add_columns("Time", "Action", "ID", "Status")
        for entry in entries:
            table.add_row(
                entry.get("timestamp", "")[:19].replace("T", " "),
                entry.get("action", ""),
                entry.get("id", ""),
                entry.get("status", "")
            )

class ExtensionApp(App):
    """A Textual app to browse and download extensions."""

    CSS = """
    Screen {
        layout: vertical;
    }
    .header {
        text-align: center;
        text-style: bold;
        margin: 1;
    }
    #stats_container {
        height: auto;
        margin: 1;
        border: solid blue;
    }
    #history_table {
        height: 1fr;
        border: solid green;
    }
    Input {
        dock: top;
        margin: 1;
    }
    #browser_select {
        height: auto;
        margin: 1;
        border: solid blue;
    }
    #search_table {
        height: 1fr;
        border: solid green;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Dashboard", id="dashboard"):
                yield Dashboard()
            with TabPane("Browser", id="browser"):
                yield Input(placeholder="Search extensions (e.g. 'adblock')...")
                yield Label("Select Browser:")
                with Horizontal(id="browser_select"):
                    with RadioSet():
                        yield RadioButton("Chrome", value=True, id="chrome")
                        yield RadioButton("Firefox", id="firefox")
                        yield RadioButton("Edge", id="edge")
                yield DataTable(id="search_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#search_table", DataTable)
        table.add_columns("Name", "ID", "Version", "Browser")
        table.cursor_type = "row"

    @work(exclusive=True, thread=True)
    def search_worker(self, browser: str, query: str) -> None:
        try:
            results = search_extension(browser, query)
            self.call_from_thread(self.update_table, results, browser)
        except Exception as e:
            self.call_from_thread(self.notify, f"Search failed: {e}", severity="error")

    def update_table(self, results, browser):
        table = self.query_one("#search_table", DataTable)
        table.clear()
        for r in results:
            table.add_row(r["name"], r["id"], r.get("version", "?"), browser)
            
        if not results:
            self.notify("No results found.", severity="warning")
        else:
            self.notify(f"Found {len(results)} results.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        if not query:
            return
        
        # Get selected browser
        radio_set = self.query_one(RadioSet)
        if radio_set.pressed_button:
            browser = radio_set.pressed_button.id
        else:
            browser = "chrome" # Default

        self.notify(f"Searching {browser} for '{query}'...")
        self.search_worker(browser, query)

    @work(thread=True)
    def download_worker(self, browser: str, ext_id: str, name: str) -> None:
        try:
            url = ext_id
            if browser == "chrome":
                url = f"https://chromewebstore.google.com/detail/{ext_id}"
            elif browser == "edge":
                url = f"https://microsoftedge.microsoft.com/addons/detail/{ext_id}"
            elif browser == "firefox":
                pass

            download_extension(browser, url, ".", show_progress=False)
            self.call_from_thread(self.notify, f"Successfully downloaded {name}!", severity="information")
            
            # Refresh dashboard if it's active?
            # Ideally yes, but for now let's keep it simple.
            
        except Exception as e:
            self.call_from_thread(self.notify, f"Download failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "search_table":
            table = event.data_table
            row = table.get_row(event.row_key)
            name = row[0]
            ext_id = row[1]
            browser = row[3]
            
            def check_confirm(confirm: bool) -> None:
                if confirm:
                    self.notify(f"Downloading {name}...")
                    self.download_worker(browser, ext_id, name)
            
            self.push_screen(ConfirmationScreen(f"Download {name}?"), check_confirm)

def run_tui():
    # Disable logging to stderr/stdout as it messes up TUI
    logging.getLogger("fetchext").setLevel(logging.CRITICAL)
    app = ExtensionApp()
    app.run()
