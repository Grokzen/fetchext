import random
import time
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import load_config

# List of modern User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

class RateLimitedSession(requests.Session):
    """
    A requests Session that enforces a minimum delay between requests.
    Thread-safe for use with ThreadPoolExecutor.
    """
    _lock = threading.Lock()
    _last_request_time = 0.0

    def __init__(self, delay: float = 0.0):
        super().__init__()
        self.delay = delay

    def request(self, method, url, *args, **kwargs):
        if self.delay > 0:
            with RateLimitedSession._lock:
                elapsed = time.time() - RateLimitedSession._last_request_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
                RateLimitedSession._last_request_time = time.time()
        return super().request(method, url, *args, **kwargs)

def get_session(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """
    Creates a requests Session with retry logic configured and a random User-Agent.
    """
    config = load_config()
    delay = config.get("network", {}).get("rate_limit_delay", 0.0)

    session = RateLimitedSession(delay=float(delay))
    
    # Set a random User-Agent
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS)
    })
    
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'HEAD', 'OPTIONS'])
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
