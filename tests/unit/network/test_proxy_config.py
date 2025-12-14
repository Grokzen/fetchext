from unittest.mock import patch
from fetchext.network import get_session


def test_get_session_with_proxies():
    """Test that get_session correctly configures proxies from config."""
    mock_config = {
        "network": {
            "proxies": {
                "http": "http://10.10.1.10:3128",
                "https": "http://10.10.1.10:1080",
            }
        }
    }

    with patch("fetchext.network.load_config", return_value=mock_config):
        session = get_session()

        assert session.proxies["http"] == "http://10.10.1.10:3128"
        assert session.proxies["https"] == "http://10.10.1.10:1080"


def test_get_session_no_proxies():
    """Test that get_session works without proxies."""
    mock_config = {"network": {}}

    with patch("fetchext.network.load_config", return_value=mock_config):
        session = get_session()
        assert session.proxies == {}
