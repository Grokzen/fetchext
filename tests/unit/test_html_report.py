import pytest
from unittest.mock import patch
from fetchext.reporter import HtmlReporter
from fetchext.core import generate_html_report

@pytest.fixture
def sample_report_data():
    return {
        "metadata": {
            "manifest": {
                "name": "Test Extension",
                "version": "1.0.0",
                "manifest_version": 3
            },
            "size": 1024
        },
        "risk_analysis": {
            "max_level": "Medium",
            "total_score": 50,
            "risky_permissions": [
                {"permission": "tabs", "level": "Medium", "score": 50, "description": "Access tabs"}
            ]
        },
        "secrets": [
            {"type": "API Key", "file": "bg.js", "line": 10, "match": "AIza..."}
        ],
        "domains": ["example.com"],
        "entropy": {
            "files": [
                {"filename": "script.js", "entropy": 5.0, "size": 500}
            ]
        }
    }

def test_html_reporter_generate(sample_report_data):
    reporter = HtmlReporter(sample_report_data)
    html = reporter.generate()
    
    assert "<!DOCTYPE html>" in html
    assert "Test Extension" in html
    assert "1.0.0" in html
    assert "risk-medium" in html
    assert "example.com" in html
    assert "AIza..." in html
    assert "riskChart" in html
    assert "new Chart" in html

def test_generate_html_report(tmp_path):
    mock_data = {"metadata": {"manifest": {"name": "Test"}}}
    
    with patch("fetchext.core.generate_unified_report", return_value=mock_data):
        file_path = tmp_path / "test.crx"
        file_path.touch()
        
        output_path = tmp_path / "report.html"
        generate_html_report(file_path, output_path)
        
        assert output_path.exists()
        assert "Test" in output_path.read_text()
