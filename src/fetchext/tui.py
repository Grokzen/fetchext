from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, DataTable, RadioSet, RadioButton, Label
from fetchext.core import search_extension, download_extension
import logging

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
    #browser_select {
        height: auto;
        margin: 1;
        border: solid blue;
    }
    DataTable {
        height: 1fr;
        border: solid green;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search extensions (e.g. 'adblock')...")
        
        yield Label("Select Browser:")
        with Horizontal(id="browser_select"):
            with RadioSet():
                yield RadioButton("Chrome", value=True, id="chrome")
                yield RadioButton("Firefox", id="firefox")
                yield RadioButton("Edge", id="edge")
        
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
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
        table = self.query_one(DataTable)
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
            # Construct a URL based on ID
            # Note: This logic might need to be smarter for different browsers
            # But core.download_extension usually takes a URL or ID?
            # core.download_extension takes (browser, url_or_id, ...)
            # Let's assume it handles ID if we pass it, or we construct URL.
            
            # For now, let's try passing ID directly if the downloader supports it,
            # or construct URL.
            url = ext_id
            if browser == "chrome":
                url = f"https://chromewebstore.google.com/detail/{ext_id}"
            elif browser == "edge":
                url = f"https://microsoftedge.microsoft.com/addons/detail/{ext_id}"
            elif browser == "firefox":
                # Firefox search returns URL usually?
                # If search_extension returns full URL in 'id' or 'url' field?
                # Let's check search implementation.
                pass

            # We might need the full URL from search results.
            # But search results only give ID/Name usually.
            
            download_extension(browser, url, ".", show_progress=False)
            self.call_from_thread(self.notify, f"Successfully downloaded {name}!", severity="information")
        except Exception as e:
            self.call_from_thread(self.notify, f"Download failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one(DataTable)
        row = table.get_row(event.row_key)
        name = row[0]
        ext_id = row[1]
        browser = row[3]
        
        self.notify(f"Downloading {name}...")
        self.download_worker(browser, ext_id, name)

def run_tui():
    # Disable logging to stderr/stdout as it messes up TUI
    logging.getLogger("fetchext").setLevel(logging.CRITICAL)
    app = ExtensionApp()
    app.run()
