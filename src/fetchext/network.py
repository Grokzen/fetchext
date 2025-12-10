import random
import time
import threading
import logging
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, TransferSpeedColumn
from .config import load_config
from .console import console
from .exceptions import NetworkError
from .utils import check_disk_space

logger = logging.getLogger(__name__)

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
        
        # Debug Logging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Request: {method} {url}")
            # Merge session headers with request headers for logging
            merged_headers = self.merge_environment_settings(url, {}, None, None, None)
            merged_headers = requests.sessions.merge_setting(merged_headers, self.headers, dict_class=dict)
            merged_headers = requests.sessions.merge_setting(merged_headers, kwargs.get('headers'), dict_class=dict)
            
            safe_headers = merged_headers.copy()
            if 'Authorization' in safe_headers:
                safe_headers['Authorization'] = 'REDACTED'
            logger.debug(f"Request Headers: {safe_headers}")

        response = super().request(method, url, *args, **kwargs)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Response: {response.status_code} {response.reason}")
            logger.debug(f"Response Headers: {dict(response.headers)}")

        return response

def get_session(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """
    Creates a requests Session with retry logic configured and a random User-Agent.
    """
    config = load_config()
    network_config = config.get("network", {})
    delay = network_config.get("rate_limit_delay", 0.0)
    proxies = network_config.get("proxies", {})

    session = RateLimitedSession(delay=float(delay))
    
    if proxies:
        session.proxies.update(proxies)
    
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

def download_file(url: str, output_path: Path, session: requests.Session = None, show_progress: bool = True, params: dict = None) -> Path:
    """
    Downloads a file from a URL to a local path, supporting resumable downloads.
    """
    if session is None:
        session = get_session()

    output_path = Path(output_path)
    resume_header = {}
    file_mode = "wb"
    downloaded_bytes = 0

    # Check for partial file
    if output_path.exists():
        downloaded_bytes = output_path.stat().st_size
        if downloaded_bytes > 0:
            resume_header = {"Range": f"bytes={downloaded_bytes}-"}
            file_mode = "ab"
            logger.info(f"Resuming download from byte {downloaded_bytes}...")

    try:
        # Make request
        headers = session.headers.copy()
        headers.update(resume_header)
        
        response = session.get(url, stream=True, headers=headers, params=params)
        
        # Handle 416 Range Not Satisfiable (file might be complete or server doesn't support range)
        if response.status_code == 416:
            logger.warning("Server returned 416 Range Not Satisfiable. Restarting download.")
            downloaded_bytes = 0
            file_mode = "wb"
            # Create a new headers dict for the retry to avoid modifying the one used in the previous call
            retry_headers = headers.copy()
            retry_headers.pop("Range", None)
            response = session.get(url, stream=True, headers=retry_headers, params=params)

        response.raise_for_status()

        # Check if server accepted the range
        is_resumed = response.status_code == 206
        if not is_resumed and downloaded_bytes > 0:
            logger.warning("Server does not support resume. Restarting download.")
            downloaded_bytes = 0
            file_mode = "wb"
            # Truncate file if we are restarting
            with output_path.open("wb") as f:
                pass

        total_size = int(response.headers.get('content-length', 0)) + downloaded_bytes
        
        # If content-length is missing, we can't show a proper progress bar total
        if total_size == downloaded_bytes and 'content-length' not in response.headers:
             total_size = None

        # Check disk space if total size is known
        if total_size:
            remaining_bytes = total_size - downloaded_bytes
            check_disk_space(output_path.parent, remaining_bytes)

        with output_path.open(file_mode) as f:
            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task(output_path.name, total=total_size, completed=downloaded_bytes)
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        if not output_path.exists() or output_path.stat().st_size == 0:
            if output_path.exists():
                output_path.unlink()
            raise NetworkError("Download failed: File is empty or does not exist.")

        return output_path

    except requests.RequestException as e:
        logger.error(f"Failed to download file: {e}")
        raise NetworkError(f"Failed to download file: {e}", original_exception=e)
