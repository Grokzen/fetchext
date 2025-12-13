import pytest
from unittest.mock import Mock, patch
from fetchext.sharing.gist import GistUploader
from fetchext.core import share_report
from fetchext.exceptions import ConfigError

@pytest.fixture
def mock_requests():
    with patch("fetchext.sharing.gist.requests") as mock:
        yield mock

def test_gist_uploader_upload(mock_requests, tmp_path):
    # Setup
    file_path = tmp_path / "report.md"
    file_path.write_text("Report content")
    
    mock_response = Mock()
    mock_response.json.return_value = {"html_url": "https://gist.github.com/123"}
    mock_response.raise_for_status.return_value = None
    mock_requests.post.return_value = mock_response
    
    uploader = GistUploader(token="fake-token")
    
    # Execute
    url = uploader.upload(file_path, description="Test Report")
    
    # Verify
    assert url == "https://gist.github.com/123"
    mock_requests.post.assert_called_once()
    args, kwargs = mock_requests.post.call_args
    assert kwargs["json"]["description"] == "Test Report"
    assert kwargs["json"]["files"]["report.md"]["content"] == "Report content"
    assert kwargs["headers"]["Authorization"] == "token fake-token"

def test_share_report_success(mock_requests, tmp_path):
    # Setup
    file_path = tmp_path / "report.md"
    file_path.write_text("Report content")
    
    mock_response = Mock()
    mock_response.json.return_value = {"html_url": "https://gist.github.com/123"}
    mock_requests.post.return_value = mock_response
    
    with patch("fetchext.core.load_config") as mock_config:
        mock_config.return_value = {
            "sharing": {
                "provider": "gist",
                "github_token": "fake-token"
            }
        }
        
        # Execute
        url = share_report(file_path)
        
        # Verify
        assert url == "https://gist.github.com/123"

def test_share_report_no_token(tmp_path):
    file_path = tmp_path / "report.md"
    file_path.write_text("Report content")
    
    with patch("fetchext.core.load_config") as mock_config:
        mock_config.return_value = {"sharing": {"provider": "gist"}}
        
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ConfigError, match="GitHub token not found"):
                share_report(file_path)
