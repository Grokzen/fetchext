from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DataTable
from fetchext.core import search_extension, download_extension
import logging

# Disable logging to stderr/stdout as it messes up TUI
logging.getLogger("fetchext").setLevel(logging.CRITICAL)

class ExtensionApp(App):
    """A Textual app to browse and download extensions."""

    CSS = """
    Screen {
        layout: vertical;
    }
    Input {
        dock: top;
        margin: 1;
    }
    DataTable {
        height: 1fr;
        border: solid green;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search Chrome extensions (e.g. 'adblock')...")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "ID", "Version", "Browser")
        table.cursor_type = "row"

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        if not query:
            return
        
        self.notify(f"Searching for '{query}'...")
        
        # Run search (synchronous for now, ideally async)
        try:
            results = search_extension("chrome", query)
            
            table = self.query_one(DataTable)
            table.clear()
            for r in results:
                table.add_row(r["name"], r["id"], r.get("version", "?"), "chrome")
                
            if not results:
                self.notify("No results found.", severity="warning")
            else:
                self.notify(f"Found {len(results)} results.")
                
        except Exception as e:
            self.notify(f"Search failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one(DataTable)
        row = table.get_row(event.row_key)
        name = row[0]
        ext_id = row[1]
        browser = row[3]
        
        self.notify(f"Downloading {name}...")
        
        # Download (synchronous)
        try:
            # Construct a URL based on ID (Chrome specific for now)
            url = f"https://chromewebstore.google.com/detail/{ext_id}"
            download_extension(browser, url, ".", show_progress=False)
            self.notify(f"Successfully downloaded {name}!", severity="information")
        except Exception as e:
            self.notify(f"Download failed: {e}", severity="error")

def run_tui():
    app = ExtensionApp()
    app.run()
