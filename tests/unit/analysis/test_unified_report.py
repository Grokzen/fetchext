import pytest
from unittest.mock import patch
from dataclasses import dataclass, field
from fetchext.core import generate_unified_report
from fetchext.exceptions import ExtensionError


@dataclass
class MockAuditReport:
    manifest_version: int = 3
    is_mv3: bool = True
    issues: list = field(default_factory=list)


@dataclass
class MockRiskReport:
    max_level: str = "Low"
    total_score: int = 0
    risky_permissions: list = field(default_factory=list)
    safe_permissions: list = field(default_factory=list)


@dataclass
class MockSecret:
    type: str = "key"
    file: str = "file.js"
    line: int = 1
    match: str = "***"


@pytest.fixture
def mock_components():
    with (
        patch("fetchext.inspector.ExtensionInspector") as mock_inspector,
        patch("fetchext.auditor.ExtensionAuditor") as mock_auditor,
        patch("fetchext.risk.RiskAnalyzer") as mock_risk,
        patch("fetchext.analysis.complexity.analyze_complexity") as mock_complexity,
        patch("fetchext.analysis.entropy.analyze_entropy") as mock_entropy,
        patch("fetchext.analysis.domains.analyze_domains") as mock_domains,
        patch("fetchext.secrets.SecretScanner") as mock_secrets,
        patch("fetchext.analysis.yara.YaraScanner") as mock_yara,
    ):
        yield {
            "inspector": mock_inspector,
            "auditor": mock_auditor,
            "risk": mock_risk,
            "complexity": mock_complexity,
            "entropy": mock_entropy,
            "domains": mock_domains,
            "secrets": mock_secrets,
            "yara": mock_yara,
        }


def test_generate_unified_report_success(mock_components, tmp_path):
    # Setup mocks
    mock_components["inspector"].return_value.get_manifest.return_value = {
        "name": "Test Ext",
        "version": "1.0",
    }

    mock_components["auditor"].return_value.audit.return_value = MockAuditReport()
    mock_components["risk"].return_value.analyze.return_value = MockRiskReport()

    mock_components["complexity"].return_value = {"average_complexity": 5}
    mock_components["entropy"].return_value = {"average_entropy": 4.5}
    mock_components["domains"].return_value = {
        "domains": ["example.com"],
        "urls": ["http://example.com"],
    }

    mock_components["secrets"].return_value.scan_extension.return_value = [MockSecret()]

    # Create dummy file
    dummy_file = tmp_path / "test.crx"
    dummy_file.write_bytes(b"dummy content")

    # Run
    report = generate_unified_report(dummy_file)

    # Assertions
    assert report["metadata"]["filename"] == "test.crx"
    assert report["metadata"]["manifest"] == {"name": "Test Ext", "version": "1.0"}
    assert "mv3_audit" in report
    assert "risk_analysis" in report
    assert report["complexity"] == {"average_complexity": 5}
    assert report["entropy"] == {"average_entropy": 4.5}
    assert report["domains"] == ["example.com"]
    assert report["urls"] == ["http://example.com"]
    assert len(report["secrets"]) == 1
    assert report["yara_matches"] is None


def test_generate_unified_report_with_yara(mock_components, tmp_path):
    # Setup mocks
    mock_components["inspector"].return_value.get_manifest.return_value = {}
    mock_components["auditor"].return_value.audit.return_value = MockAuditReport()
    mock_components["risk"].return_value.analyze.return_value = MockRiskReport()
    mock_components["complexity"].return_value = {}
    mock_components["entropy"].return_value = {}
    mock_components["domains"].return_value = {"domains": [], "urls": []}
    mock_components["secrets"].return_value.scan_extension.return_value = []

    mock_components["yara"].return_value.scan_archive.return_value = {
        "file.js": [{"rule": "suspicious"}]
    }

    # Create dummy file
    dummy_file = tmp_path / "test.crx"
    dummy_file.write_bytes(b"dummy content")
    yara_rules = tmp_path / "rules.yar"
    yara_rules.touch()

    # Run
    report = generate_unified_report(dummy_file, yara_rules=yara_rules)

    # Assertions
    assert report["yara_matches"] == {"file.js": [{"rule": "suspicious"}]}
    mock_components["yara"].assert_called_once_with(yara_rules)


def test_generate_unified_report_file_not_found():
    with pytest.raises(ExtensionError, match="File not found"):
        generate_unified_report("nonexistent.crx")
