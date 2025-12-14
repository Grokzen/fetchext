import pytest
from unittest.mock import patch
from pathlib import Path
from datetime import datetime
from fetchext.interface.reporter import MarkdownReporter
from fetchext.security.risk import RiskReport, PermissionRisk


@pytest.fixture
def mock_inspector():
    with patch("fetchext.interface.reporter.ExtensionInspector") as mock:
        yield mock.return_value


@pytest.fixture
def mock_risk_analyzer():
    with patch("fetchext.interface.reporter.RiskAnalyzer") as mock:
        yield mock.return_value


class TestMarkdownReporter:
    def test_init_file_not_found(self):
        from fetchext.core.exceptions import ExtensionError

        with pytest.raises(ExtensionError):
            MarkdownReporter(Path("non_existent.crx"))

    def test_generate_report(self, fs, mock_inspector, mock_risk_analyzer):
        # Setup fake file
        fake_file = Path("test.crx")
        fs.create_file(fake_file, contents="fake content")

        # Setup mocks
        mock_inspector.inspect.return_value = {
            "manifest": {
                "name": "Test Ext",
                "version": "1.0",
                "description": "A test extension",
                "author": "Tester",
                "manifest_version": 3,
            },
            "timeline": [
                {
                    "filename": "manifest.json",
                    "datetime": datetime(2023, 1, 1),
                    "size": 100,
                },
                {
                    "filename": "background.js",
                    "datetime": datetime(2023, 1, 1),
                    "size": 200,
                },
                {
                    "filename": "icons/icon.png",
                    "datetime": datetime(2023, 1, 1),
                    "size": 300,
                },
            ],
            "errors": [],
            "valid": True,
        }

        mock_risk_analyzer.analyze.return_value = RiskReport(
            total_score=10,
            max_level="High",
            risky_permissions=[PermissionRisk("tabs", 7, "High", "Access tabs")],
            safe_permissions=["storage"],
        )

        reporter = MarkdownReporter(fake_file)
        report = reporter.generate()

        assert "# Extension Report: Test Ext" in report
        assert "**Version** | 1.0" in report
        assert "**Overall Risk Level:** 🟠 **High**" in report
        assert "| `tabs` | High | 7 | Access tabs |" in report
        assert "`storage`" in report
        assert "manifest.json" in report
        assert "background.js" in report

    def test_save_report(self, fs, mock_inspector, mock_risk_analyzer):
        fake_file = Path("test.crx")
        fs.create_file(fake_file, contents="fake content")

        mock_inspector.inspect.return_value = {
            "manifest": {"name": "Test"},
            "timeline": [],
            "errors": [],
            "valid": True,
        }
        mock_risk_analyzer.analyze.return_value = RiskReport(0, "Safe")

        reporter = MarkdownReporter(fake_file)
        output_path = Path("report.md")
        reporter.save(output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "# Extension Report: Test" in content

    def test_tree_generation(self, fs):
        # Test the internal tree generation logic
        fake_file = Path("test.crx")
        fs.create_file(fake_file)

        # We don't need full mocks for this unit test of a private method if we access it directly,
        # but we need to instantiate the class.
        # We can just patch the init to avoid side effects or use the mocks.
        with (
            patch("fetchext.interface.reporter.ExtensionInspector"),
            patch("fetchext.interface.reporter.RiskAnalyzer"),
        ):
            reporter = MarkdownReporter(fake_file)

            file_list = ["a.txt", "b/c.txt", "b/d.txt"]
            tree_text = reporter._generate_tree_text(file_list)

            assert "a.txt" in tree_text
            assert "b" in tree_text
            assert "c.txt" in tree_text
            assert "d.txt" in tree_text
            assert "├──" in tree_text or "└──" in tree_text
