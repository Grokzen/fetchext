from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    @abstractmethod
    def extract_id(self, url):
        """Extract the extension ID or slug from the URL."""
        pass

    @abstractmethod
    def download(self, extension_id, output_dir):
        """Download the extension and return the file path."""
        pass
