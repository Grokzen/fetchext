import requests
from requests.adapters import HTTPAdapter
from fetchext.network import get_session

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
