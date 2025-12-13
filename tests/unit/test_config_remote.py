import pytest
from unittest.mock import Mock, patch
from fetchext.commands.config import handle_config_remote
from fetchext.constants import ExitCode

@pytest.fixture
def mock_args():
    args = Mock()
    args.url = "https://example.com/config.toml"
    return args

def test_handle_config_remote_success(mock_args, tmp_path):
    toml_content = 'theme = "dark"\n[network]\ntimeout = 30'
    
    with patch("requests.get") as mock_get, \
         patch("fetchext.config.get_config_path") as mock_get_path:
        
        # Setup mocks
        mock_response = Mock()
        mock_response.text = toml_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        config_file = tmp_path / "config.toml"
        mock_get_path.return_value = config_file
        
        # Run
        handle_config_remote(mock_args)
        
        # Verify
        mock_get.assert_called_once_with("https://example.com/config.toml", timeout=10)
        assert config_file.exists()
        assert b'theme = "dark"' in config_file.read_bytes()

def test_handle_config_remote_network_error(mock_args):
    import requests
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        with pytest.raises(SystemExit) as exc:
            handle_config_remote(mock_args)
        assert exc.value.code == ExitCode.NETWORK

def test_handle_config_remote_invalid_toml(mock_args):
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = "invalid toml content ["
        mock_get.return_value = mock_response
        
        with pytest.raises(SystemExit) as exc:
            handle_config_remote(mock_args)
        assert exc.value.code == ExitCode.CONFIG
