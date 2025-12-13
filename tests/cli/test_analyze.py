import pytest
import sys
from unittest.mock import patch, MagicMock
from fetchext.cli import main

class TestAnalyzeCLI:
    def test_analyze_complexity(self):
        with patch.object(sys, 'argv', ['fext', 'analyze', 'complexity', 'test.crx']), \
             patch('fetchext.analysis.complexity.analyze_complexity') as mock_analyze:
            
            mock_analyze.return_value = {
                "average_complexity": 1.0,
                "max_complexity": 1,
                "total_functions": 1,
                "high_complexity_functions": []
            }
            
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_analyze.assert_called_once()

    def test_analyze_entropy(self):
        with patch.object(sys, 'argv', ['fext', 'analyze', 'entropy', 'test.crx']), \
             patch('fetchext.analysis.entropy.analyze_entropy') as mock_analyze:
            
            mock_analyze.return_value = {
                "average_entropy": 5.0,
                "files": []
            }
            
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_analyze.assert_called_once()

    def test_analyze_domains(self):
        with patch.object(sys, 'argv', ['fext', 'analyze', 'domains', 'test.crx']), \
             patch('fetchext.analysis.domains.analyze_domains') as mock_analyze:
            
            mock_analyze.return_value = {
                "domains": [],
                "urls": []
            }
            
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_analyze.assert_called_once()

    def test_analyze_secrets(self):
        with patch.object(sys, 'argv', ['fext', 'analyze', 'secrets', 'test.crx']), \
             patch('fetchext.secrets.SecretScanner') as MockScanner:
            
            mock_instance = MockScanner.return_value
            mock_instance.scan_extension.return_value = []
            
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            mock_instance.scan_extension.assert_called_once()

    def test_analyze_yara(self):
        with patch.object(sys, 'argv', ['fext', 'analyze', 'yara', 'rules.yar', 'test.crx']), \
             patch('fetchext.analysis.yara.YaraScanner') as MockScanner:
            
            mock_instance = MockScanner.return_value
            mock_instance.scan_archive.return_value = {}
            
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            MockScanner.assert_called_once()
            mock_instance.scan_archive.assert_called_once()
