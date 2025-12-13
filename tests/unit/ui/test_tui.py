import pytest
from unittest.mock import patch

# Skip if textual is not installed
textual = pytest.importorskip("textual")
from textual.widgets import Input, DataTable  # noqa: E402
from fetchext.tui import ExtensionApp  # noqa: E402

@pytest.mark.asyncio
async def test_tui_app_structure():
    app = ExtensionApp()
    async with app.run_test():
        assert app.query_one(Input)
        assert app.query_one(DataTable)

@pytest.mark.asyncio
async def test_tui_search_submission():
    with patch("fetchext.tui.search_extension") as mock_search:
        mock_search.return_value = [
            {"name": "Test Ext", "id": "abc", "version": "1.0"}
        ]
        
        app = ExtensionApp()
        async with app.run_test() as pilot:
            input_widget = app.query_one(Input)
            input_widget.focus()
            input_widget.value = "test"
            await pilot.press("enter")
            
            # Check if search was called
            mock_search.assert_called_with("chrome", "test")
            
            # Check if table has rows
            table = app.query_one(DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0)[0] == "Test Ext"
