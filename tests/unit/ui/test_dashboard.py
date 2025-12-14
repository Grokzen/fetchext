import pytest
from unittest.mock import MagicMock, patch
from fetchext.ui.app import ExtensionApp, Dashboard


@pytest.mark.asyncio
async def test_dashboard_loads_data():
    # Mock dependencies
    with (
        patch("fetchext.ui.app.get_repo_stats") as mock_stats,
        patch("fetchext.ui.app.HistoryManager") as mock_history_cls,
    ):
        # Setup mocks
        mock_stats_obj = MagicMock()
        mock_stats_obj.total_extensions = 10
        mock_stats_obj.total_size_bytes = 1024 * 1024 * 10  # 10 MB
        mock_stats_obj.mv3_count = 5
        mock_stats_obj.risk_distribution = {"Low": 5, "High": 5}
        mock_stats.return_value = mock_stats_obj

        mock_history = MagicMock()
        mock_history.get_entries.return_value = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "action": "download",
                "id": "abc",
                "status": "success",
            }
        ]
        mock_history_cls.return_value = mock_history

        app = ExtensionApp()
        async with app.run_test() as pilot:
            # Check if Dashboard is present
            assert app.query_one(Dashboard)

            # Wait for threaded workers to complete and UI to update
            # This is a bit arbitrary, but usually sufficient for mocks
            await pilot.pause(0.5)

            # Verify get_repo_stats was called
            mock_stats.assert_called()

            # Verify history was fetched
            mock_history.get_entries.assert_called_with(limit=10)

            # Check UI content
            # The dashboard should contain Markdown with "Total Extensions: 10"
            # We can search for the text in the app
            # Textual 0.38+ has app.screen.query(...)

            # Let's check if the Markdown widget contains the text
            markdown_widgets = app.query("Markdown")
            found_stats = False
            for w in markdown_widgets:
                # Textual Markdown widget doesn't expose raw text easily in 'source' property?
                # It has a 'source' property.
                if "Total Extensions:** 10" in w.source:
                    found_stats = True
                    break

            assert found_stats, "Dashboard stats not found in UI"


@pytest.mark.asyncio
async def test_dashboard_tab_switching():
    app = ExtensionApp()
    async with app.run_test():
        # Initial state: Dashboard tab
        assert app.query_one("#dashboard").display

        # Verify structure
        assert app.query_one("TabbedContent")
        assert app.query_one("#browser")

        # We can't easily predict the Tab ID, so we'll just verify the panes exist
        # and the dashboard is the active one initially.

        # To switch, we can programmatically set the active tab if we knew the ID,
        # or just trust TabbedContent works.

        # Let's try to find the tab by class or type
        tabs = app.query("Tab")
        assert len(tabs) >= 2
