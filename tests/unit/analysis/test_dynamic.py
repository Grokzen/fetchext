import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fetchext.analysis.dynamic import DynamicAnalyzer
from fetchext.exceptions import AnalysisError


@pytest.fixture
def mock_playwright():
    # Patch PLAYWRIGHT_AVAILABLE to True
    with patch("fetchext.analysis.dynamic.PLAYWRIGHT_AVAILABLE", True):
        # Patch async_playwright
        with patch("fetchext.analysis.dynamic.async_playwright", create=True) as mock:
            yield mock


@pytest.fixture
def analyzer(tmp_path):
    ext_path = tmp_path / "ext"
    ext_path.mkdir()
    output_dir = tmp_path / "output"
    return DynamicAnalyzer(ext_path, output_dir)


@pytest.mark.asyncio
async def test_run_success(analyzer, mock_playwright):
    # Mock playwright context manager
    mock_p = AsyncMock()
    mock_playwright.return_value.__aenter__.return_value = mock_p

    # Mock browser context
    mock_context = AsyncMock()
    mock_p.chromium.launch_persistent_context.return_value = mock_context

    # Mock page
    mock_page = AsyncMock()
    # page.on is synchronous
    mock_page.on = MagicMock()
    mock_context.new_page.return_value = mock_page

    # Mock background pages
    mock_bg_page = AsyncMock()
    # background page screenshot is async, so keep it as AsyncMock (default)
    mock_bg_page.url = "chrome-extension://abc/background.html"
    mock_context.background_pages = [mock_bg_page]

    await analyzer.run(duration=0)

    # Verify launch args
    mock_p.chromium.launch_persistent_context.assert_called_once()
    call_kwargs = mock_p.chromium.launch_persistent_context.call_args.kwargs
    assert "args" in call_kwargs
    assert any("--load-extension" in arg for arg in call_kwargs["args"])

    # Verify screenshots
    mock_page.screenshot.assert_called()
    mock_bg_page.screenshot.assert_called()

    # Verify data saved
    assert (analyzer.output_dir / "logs.json").exists()
    assert (analyzer.output_dir / "network.json").exists()


@pytest.mark.asyncio
async def test_run_missing_extension(tmp_path):
    # We need to patch PLAYWRIGHT_AVAILABLE here too, or ensure it fails correctly
    with patch("fetchext.analysis.dynamic.PLAYWRIGHT_AVAILABLE", True):
        analyzer = DynamicAnalyzer(tmp_path / "missing", tmp_path / "output")
        with pytest.raises(AnalysisError, match="Extension path not found"):
            await analyzer.run()


def test_monitor_console(analyzer):
    mock_page = MagicMock()
    analyzer._monitor_console(mock_page)

    # Simulate console event
    callback = mock_page.on.call_args[0][1]
    mock_msg = MagicMock()
    mock_msg.type = "log"
    mock_msg.text = "Hello"
    mock_msg.location = "script.js:1"

    callback(mock_msg)

    assert len(analyzer.logs) == 1
    assert analyzer.logs[0]["text"] == "Hello"


def test_monitor_network(analyzer):
    mock_page = MagicMock()
    analyzer._monitor_network(mock_page)

    # Simulate request event
    callback = mock_page.on.call_args[0][1]
    mock_req = MagicMock()
    mock_req.url = "https://example.com"
    mock_req.method = "GET"
    mock_req.resource_type = "xhr"

    callback(mock_req)

    assert len(analyzer.network_activity) == 1
    assert analyzer.network_activity[0]["url"] == "https://example.com"
