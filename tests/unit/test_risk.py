import json
from unittest.mock import MagicMock, patch
from fetchext.risk import RiskAnalyzer

def create_mock_zip(manifest):
    zf = MagicMock()
    zf.read.side_effect = lambda name: json.dumps(manifest).encode() if name == "manifest.json" else b""
    return zf

def test_risk_analysis_critical():
    manifest = {
        "permissions": ["<all_urls>", "tabs", "storage"]
    }
    
    with patch("fetchext.risk.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = create_mock_zip(manifest)
        
        analyzer = RiskAnalyzer()
        report = analyzer.analyze("dummy.crx")
        
        assert report.max_level == "Critical"
        assert report.total_score == 10 + 7 + 4 # 21
        
        perms = {p.permission: p for p in report.risky_permissions}
        assert "<all_urls>" in perms
        assert perms["<all_urls>"].level == "Critical"
        assert "tabs" in perms
        assert perms["tabs"].level == "High"

def test_risk_analysis_safe():
    manifest = {
        "permissions": ["alarms", "idle"]
    }
    
    with patch("fetchext.risk.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = create_mock_zip(manifest)
        
        analyzer = RiskAnalyzer()
        report = analyzer.analyze("dummy.crx")
        
        assert report.max_level == "Low"
        assert report.total_score == 2

def test_risk_analysis_host_permissions():
    manifest = {
        "host_permissions": ["*://*.google.com/*"]
    }
    
    with patch("fetchext.risk.open_extension_archive") as mock_open:
        mock_open.return_value.__enter__.return_value = create_mock_zip(manifest)
        
        analyzer = RiskAnalyzer()
        report = analyzer.analyze("dummy.crx")
        
        assert report.max_level == "High" # *:// pattern
        assert len(report.risky_permissions) == 1
        assert report.risky_permissions[0].permission == "*://*.google.com/*"
