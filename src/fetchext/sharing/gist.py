import requests
from pathlib import Path
from typing import Optional
from .base import BaseUploader


class GistUploader(BaseUploader):
    """Uploads reports to GitHub Gist."""

    def __init__(self, token: str, public: bool = False):
        self.token = token
        self.public = public
        self.api_url = "https://api.github.com/gists"

    def upload(self, file_path: Path, description: Optional[str] = None) -> str:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        filename = file_path.name

        # Gist API payload
        payload = {
            "description": description or f"Report shared via fetchext: {filename}",
            "public": self.public,
            "files": {filename: {"content": content}},
        }

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.post(
            self.api_url, json=payload, headers=headers, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data["html_url"]
