from abc import ABC, abstractmethod
from ..client import NetworkClient

class BaseDownloader(ABC):
    def __init__(self):
        self.client = NetworkClient()

    @abstractmethod
    def extract_id(self, url):
        """Extract the extension ID or slug from the URL."""
        pass

    @abstractmethod
    def download(self, extension_id, output_dir, show_progress=True):
        """Download the extension and return the file path."""
        pass

    def get_latest_version(self, extension_id):
        """Get the latest version of the extension from the store."""
        raise NotImplementedError("Version check not implemented for this browser")
