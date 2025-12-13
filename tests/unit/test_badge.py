from unittest.mock import Mock, patch
from fetchext.reporter import BadgeGenerator
from fetchext.commands.badge import handle_badge

def test_badge_generator_svg():
    svg = BadgeGenerator.generate("test", "pass", "green")
    assert "<svg" in svg
    assert "test" in svg
    assert "pass" in svg
    assert "#4c1" in svg  # green hex

def test_handle_badge(tmp_path):
    # Mock args
    args = Mock()
    file_path = tmp_path / "test.crx"
    file_path.touch()
    args.file = file_path
    args.output_dir = tmp_path
    
    # Mock dependencies
    with patch("fetchext.commands.badge.ExtensionInspector") as MockInspector, \
         patch("fetchext.commands.badge.RiskAnalyzer") as MockAnalyzer, \
         patch("fetchext.commands.badge.scan_licenses") as mock_scan:
        
        # Setup Inspector
        inspector = MockInspector.return_value
        inspector.get_manifest.return_value = {"version": "1.2.3"}
        
        # Setup Analyzer
        analyzer = MockAnalyzer.return_value
        report = Mock()
        report.max_level = "Safe"
        analyzer.analyze.return_value = report
        
        # Setup License
        mock_scan.return_value = {"MIT": ["LICENSE"]}
        
        # Run
        handle_badge(args)
        
        # Verify files created
        assert (tmp_path / "test_version.svg").exists()
        assert (tmp_path / "test_risk.svg").exists()
        assert (tmp_path / "test_license.svg").exists()
        
        # Verify content
        assert "1.2.3" in (tmp_path / "test_version.svg").read_text()
        assert "Safe" in (tmp_path / "test_risk.svg").read_text()
        assert "MIT" in (tmp_path / "test_license.svg").read_text()
