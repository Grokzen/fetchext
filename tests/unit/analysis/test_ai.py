import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from fetchext.analysis.ai import AIClient, summarize_extension

@pytest.fixture
def mock_config():
    return {
        "ai": {
            "enabled": True,
            "api_key": "test-key",
            "base_url": "https://api.test.com",
            "model": "test-model"
        }
    }

def test_ai_client_init(mock_config):
    client = AIClient(mock_config["ai"])
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.test.com"
    assert client.model == "test-model"

@patch("requests.post")
def test_ai_client_chat_completion(mock_post, mock_config):
    client = AIClient(mock_config["ai"])
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test summary"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    summary = client.chat_completion("Test prompt")
    
    assert summary == "Test summary"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "test-model"

@patch("fetchext.analysis.ai.load_config")
@patch("fetchext.analysis.ai.AIClient")
def test_summarize_extension_disabled(mock_client_cls, mock_load_config, fs):
    mock_load_config.return_value = {"ai": {"enabled": False}}
    fs.create_file("test.zip")
    
    with pytest.raises(RuntimeError, match="AI analysis is disabled"):
        summarize_extension(Path("test.zip"))

@patch("fetchext.analysis.ai.load_config")
@patch("fetchext.analysis.ai.AIClient")
def test_summarize_extension_success(mock_client_cls, mock_load_config, fs):
    mock_load_config.return_value = {"ai": {"enabled": True}}
    
    mock_client = Mock()
    mock_client.chat_completion.return_value = "Summary"
    mock_client_cls.return_value = mock_client
    
    # Create a fake zip file
    import zipfile
    zip_path = Path("test.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", '{"name": "Test", "version": "1.0", "background": {"scripts": ["background.js"]}}')
        zf.writestr("background.js", "console.log('bg');")
    
    summary = summarize_extension(zip_path, show_progress=False)
    
    assert summary == "Summary"
    mock_client.chat_completion.assert_called_once()
    prompt = mock_client.chat_completion.call_args[0][0]
    assert "manifest.json" in prompt
    assert "background.js" in prompt
