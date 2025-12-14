import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fetchext.tui import ExtensionApp, ConfirmationScreen


@pytest.fixture
def mock_core():
    with (
        patch("fetchext.tui.search_extension") as mock_search,
        patch("fetchext.tui.download_extension") as mock_download,
        patch("fetchext.tui.get_repo_stats") as mock_stats,
        patch("fetchext.tui.HistoryManager") as mock_history,
    ):
        # Setup default returns
        mock_search.return_value = [{"name": "Test Ext", "id": "abc", "version": "1.0"}]

        mock_stats_obj = MagicMock()
        mock_stats_obj.total_extensions = 10
        mock_stats_obj.total_size_bytes = 1024 * 1024 * 10
        mock_stats_obj.mv3_count = 5
        mock_stats_obj.risk_distribution = {"Low": 5, "High": 5}
        mock_stats.return_value = mock_stats_obj

        mock_history.return_value.get_entries.return_value = []

        yield mock_search, mock_download, mock_stats, mock_history


@pytest.mark.asyncio
async def test_app_startup(mock_core):
    app = ExtensionApp()
    async with app.run_test() as pilot:
        # Check if Dashboard tab is active
        assert app.query_one("TabbedContent").active == "dashboard"

        # Check if stats are loaded (might need a small wait for worker)
        await pilot.pause()
        await asyncio.sleep(0.2)  # Give worker time
        assert "**Total Extensions:** 10" in app.query_one("Markdown").source


@pytest.mark.asyncio
async def test_search_flow(mock_core):
    mock_search, _, _, _ = mock_core
    app = ExtensionApp()
    async with app.run_test() as pilot:
        # Switch to Browser tab programmatically to ensure it's active
        app.query_one("TabbedContent").active = "browser"
        await pilot.pause()

        # Type query
        await pilot.click("Input")
        await pilot.press("t", "e", "s", "t", "enter")

        # Wait for worker
        await pilot.pause()
        await asyncio.sleep(0.2)

        # Verify search called
        mock_search.assert_called_with("chrome", "test")

        # Verify table populated
        table = app.query_one("#search_table")
        assert table.row_count == 1
        assert table.get_row_at(0)[0] == "Test Ext"


@pytest.mark.asyncio
async def test_browser_selection(mock_core):
    mock_search, _, _, _ = mock_core
    app = ExtensionApp()
    async with app.run_test() as pilot:
        app.query_one("TabbedContent").active = "browser"
        await pilot.pause()

        # Select Firefox
        await pilot.click("#firefox")

        # Search
        await pilot.click("Input")
        await pilot.press("a", "enter")

        await pilot.pause()
        await asyncio.sleep(0.2)

        mock_search.assert_called_with("firefox", "a")


@pytest.mark.asyncio
async def test_download_flow(mock_core):
    _, mock_download, _, _ = mock_core
    app = ExtensionApp()
    async with app.run_test() as pilot:
        app.query_one("TabbedContent").active = "browser"
        await pilot.pause()

        # Perform search to populate table
        await pilot.click("Input")
        await pilot.press("a", "enter")
        await pilot.pause()
        await asyncio.sleep(0.2)

        # Click row to download
        table = app.query_one("#search_table")
        assert table.row_count > 0

        # Focus table and select row
        table.focus()
        table.move_cursor(row=0)
        await pilot.press("enter")

        # Wait for confirmation dialog
        await pilot.pause()
        await asyncio.sleep(0.2)

        # Check if modal is active and has correct message
        assert isinstance(app.screen, ConfirmationScreen)
        assert app.screen.message == "Download Test Ext?"

        # Click Yes
        await pilot.click("#yes")

        await pilot.pause()
        await asyncio.sleep(0.2)

        # Verify download called
        mock_download.assert_called()
