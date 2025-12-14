import logging
from unittest.mock import MagicMock, patch
from fetchext.network.network import RateLimitedSession


def test_debug_logging(caplog):
    caplog.set_level(logging.DEBUG)

    session = RateLimitedSession()

    # Mock the actual request to avoid network calls
    with patch("requests.Session.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        session.get("http://example.com", headers={"Authorization": "Secret"})

        # Check logs
        assert "Request: GET http://example.com" in caplog.text
        assert "Request Headers:" in caplog.text
        assert "REDACTED" in caplog.text
        assert "Secret" not in caplog.text
        assert "Response: 200 OK" in caplog.text
        assert "Response Headers:" in caplog.text
        assert "Content-Type" in caplog.text


def test_no_debug_logging(caplog):
    caplog.set_level(logging.INFO)

    session = RateLimitedSession()

    with patch("requests.Session.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        session.get("http://example.com")

        assert "Request: GET" not in caplog.text
