import time
import requests
from unittest.mock import patch, MagicMock
from requests.adapters import HTTPAdapter
from fetchext.network import get_session, USER_AGENTS, RateLimitedSession

def test_get_session_defaults():
    session = get_session()
    assert isinstance(session, requests.Session)
    
    adapter = session.get_adapter("https://google.com")
    assert isinstance(adapter, HTTPAdapter)
    
    # Check defaults
    assert adapter.max_retries.total == 3
    assert adapter.max_retries.backoff_factor == 1.0
    assert 500 in adapter.max_retries.status_forcelist
    assert 502 in adapter.max_retries.status_forcelist
    assert 503 in adapter.max_retries.status_forcelist
    assert 504 in adapter.max_retries.status_forcelist

def test_get_session_custom_config():
    session = get_session(retries=5, backoff_factor=0.5, status_forcelist=(500,))
    
    adapter = session.get_adapter("https://google.com")
    
    assert adapter.max_retries.total == 5
    assert adapter.max_retries.backoff_factor == 0.5
    assert 500 in adapter.max_retries.status_forcelist
    assert 502 not in adapter.max_retries.status_forcelist

def test_session_mounts():
    session = get_session()
    assert session.get_adapter("http://example.com") is session.get_adapter("https://example.com")

def test_get_session_has_user_agent():
    """Test that the session has a User-Agent header."""
    session = get_session()
    assert "User-Agent" in session.headers
    assert session.headers["User-Agent"] in USER_AGENTS

def test_get_session_rotates_user_agent():
    """Test that multiple calls to get_session return different User-Agents (probabilistic)."""
    # This test is probabilistic, but with 8 agents, the chance of getting the same one 
    # 10 times in a row is extremely low.
    agents = set()
    for _ in range(20):
        session = get_session()
        agents.add(session.headers["User-Agent"])
    
    # We expect to see at least 2 different agents
    assert len(agents) > 1

def test_rate_limited_session():
    # Set a delay of 0.1 seconds
    session = RateLimitedSession(delay=0.1)
    
    start_time = time.time()
    
    # Mock the super().request to avoid actual network calls
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = MagicMock(status_code=200)
        
        # Make 3 requests
        session.get("http://example.com")
        session.get("http://example.com")
        session.get("http://example.com")
        
    end_time = time.time()
    duration = end_time - start_time
    
    # Should take at least 0.2 seconds (wait before 2nd and 3rd request)
    assert duration >= 0.2

def test_get_session_config():
    with patch("fetchext.network.load_config") as mock_config:
        mock_config.return_value = {"network": {"rate_limit_delay": 0.5}}
        
        session = get_session()
        assert isinstance(session, RateLimitedSession)
        assert session.delay == 0.5

def test_get_session_default_delay():
    with patch("fetchext.network.load_config") as mock_config:
        mock_config.return_value = {}
        
        session = get_session()
        assert isinstance(session, RateLimitedSession)
        assert session.delay == 0.0
