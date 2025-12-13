import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from fetchext.risk import RiskAnalyzer

@pytest.fixture
def mock_extension_archive():
    with patch("fetchext.risk.open_extension_archive") as mock_open:
        mock_zf = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_zf
        yield mock_zf

def test_risk_combination_session_hijacking(mock_extension_archive):
    # tabs + cookies + <all_urls>
    manifest = {
        "permissions": ["tabs", "cookies", "<all_urls>"]
    }
    mock_extension_archive.read.return_value = json.dumps(manifest).encode("utf-8")
    
    analyzer = RiskAnalyzer()
    report = analyzer.analyze(Path("dummy.crx"))
    
    # Check for combination risk
    combination_found = False
    for risk in report.risky_permissions:
        if risk.permission == "COMBINATION" and "Session Hijacking" in risk.description:
            combination_found = True
            assert risk.score == 20
            assert risk.level == "Critical"
            break
    
    assert combination_found
    # Base scores: tabs(7) + cookies(9) + all_urls(10) = 26
    # Bonus: 20
    # Total should be >= 46
    assert report.total_score >= 46

def test_risk_combination_mitm(mock_extension_archive):
    # webRequest + webRequestBlocking + *://*/*
    manifest = {
        "permissions": ["webRequest", "webRequestBlocking"],
        "host_permissions": ["*://*/*"]
    }
    mock_extension_archive.read.return_value = json.dumps(manifest).encode("utf-8")
    
    analyzer = RiskAnalyzer()
    report = analyzer.analyze(Path("dummy.crx"))
    
    combination_found = False
    for risk in report.risky_permissions:
        if risk.permission == "COMBINATION" and "Man-in-the-Middle" in risk.description:
            combination_found = True
            break
            
    assert combination_found

def test_risk_no_combination(mock_extension_archive):
    # tabs only
    manifest = {
        "permissions": ["tabs"]
    }
    mock_extension_archive.read.return_value = json.dumps(manifest).encode("utf-8")
    
    analyzer = RiskAnalyzer()
    report = analyzer.analyze(Path("dummy.crx"))
    
    combination_found = False
    for risk in report.risky_permissions:
        if risk.permission == "COMBINATION":
            combination_found = True
            break
            
    assert not combination_found
    assert report.total_score == 7 # tabs score
