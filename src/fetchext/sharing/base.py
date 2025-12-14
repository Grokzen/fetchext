from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseUploader(ABC):
    """Abstract base class for report uploaders."""

    @abstractmethod
    def upload(self, file_path: Path, description: Optional[str] = None) -> str:
        """
        Upload the file and return the public URL.

        Args:
            file_path: Path to the file to upload.
            description: Optional description for the upload.

        Returns:
            str: The URL of the uploaded content.

        Raises:
            Exception: If the upload fails.
        """
        pass
