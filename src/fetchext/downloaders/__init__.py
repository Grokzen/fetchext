from .chrome import ChromeDownloader
from .edge import EdgeDownloader
from .firefox import FirefoxDownloader

def get_downloader_for_browser(browser_name):
    if browser_name in ["chrome", "c"]:
        return ChromeDownloader
    elif browser_name in ["edge", "e"]:
        return EdgeDownloader
    elif browser_name in ["firefox", "f"]:
        return FirefoxDownloader
    return None

__all__ = ["ChromeDownloader", "EdgeDownloader", "FirefoxDownloader", "get_downloader_for_browser"]
