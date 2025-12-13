import pytest
from unittest.mock import MagicMock
import requests
from fetchext.network import download_file
from fetchext.exceptions import NetworkError

def test_download_403_error(fs):
    output_path = "test.crx"
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden", response=mock_response)
    mock_session.get.return_value = mock_response
    
    with pytest.raises(NetworkError, match=r"Access Denied \(403\)"):
        download_file("http://example.com", output_path, session=mock_session)

def test_download_429_error(fs):
    output_path = "test.crx"
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests", response=mock_response)
    mock_session.get.return_value = mock_response
    
    with pytest.raises(NetworkError, match=r"Rate Limit Exceeded \(429\)"):
        download_file("http://example.com", output_path, session=mock_session)

def test_download_other_http_error(fs):
    output_path = "test.crx"
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error", response=mock_response)
    mock_session.get.return_value = mock_response
    
    with pytest.raises(NetworkError, match="HTTP Error"):
        download_file("http://example.com", output_path, session=mock_session)
