import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
from fetchext.core import download_extension, extract_extension, generate_unified_report
from fetchext.hooks import HookContext


@pytest.fixture
def mock_downloader():
    with patch("fetchext.core.get_downloader") as mock:
        downloader = MagicMock()
        downloader.extract_id.return_value = "test_id"
        downloader.download.return_value = Path("test.crx")
        mock.return_value = downloader
        yield mock


@pytest.fixture
def mock_hook_manager():
    with patch("fetchext.core.HookManager") as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager


def test_download_extension_hooks(mock_downloader, mock_hook_manager, tmp_path):
    # Test that hooks are called
    download_extension("chrome", "http://example.com", tmp_path, show_progress=False)

    # Verify pre_download call
    assert mock_hook_manager.run_hook.call_count >= 2
    args, _ = mock_hook_manager.run_hook.call_args_list[0]
    assert args[0] == "pre_download"
    assert isinstance(args[1], HookContext)
    assert args[1].extension_id == "test_id"

    # Verify post_download call
    args, _ = mock_hook_manager.run_hook.call_args_list[1]
    assert args[0] == "post_download"
    assert isinstance(args[1], HookContext)


def test_download_extension_cancellation(mock_downloader, mock_hook_manager, tmp_path):
    # Setup hook to cancel
    def cancel_hook(name, ctx):
        if name == "pre_download":
            ctx.cancel = True

    mock_hook_manager.run_hook.side_effect = cancel_hook

    result = download_extension(
        "chrome", "http://example.com", tmp_path, show_progress=False
    )

    assert result is None
    # Downloader should NOT be called
    mock_downloader.return_value.download.assert_not_called()


def test_extract_extension_hooks(mock_hook_manager, tmp_path):
    # Create a dummy zip file
    import zipfile

    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", "{}")

    extract_extension(zip_path, tmp_path / "extracted", show_progress=False)

    # Verify post_extract call
    mock_hook_manager.run_hook.assert_called_with("post_extract", ANY)


def test_analysis_hooks(mock_hook_manager, tmp_path):
    # Create dummy file
    f = tmp_path / "test.crx"
    f.write_text("dummy")

    from dataclasses import dataclass

    @dataclass
    class DummyReport:
        pass

    # Mock all the analysis functions to avoid real work
    with (
        patch("fetchext.inspector.ExtensionInspector"),
        patch("fetchext.auditor.ExtensionAuditor") as mock_auditor,
        patch("fetchext.risk.RiskAnalyzer") as mock_risk,
        patch("fetchext.analysis.complexity.analyze_complexity"),
        patch("fetchext.analysis.entropy.analyze_entropy"),
        patch(
            "fetchext.analysis.domains.analyze_domains",
            return_value={"domains": [], "urls": []},
        ),
        patch("fetchext.secrets.SecretScanner") as mock_secrets,
    ):
        mock_auditor.return_value.audit.return_value = DummyReport()
        mock_risk.return_value.analyze.return_value = DummyReport()
        mock_secrets.return_value.scan_extension.return_value = []

        generate_unified_report(f)

        # Verify calls
        calls = [args[0] for args, _ in mock_hook_manager.run_hook.call_args_list]
        assert "pre_analysis" in calls
        assert "post_analysis" in calls
