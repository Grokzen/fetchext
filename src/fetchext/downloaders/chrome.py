import re
import logging
import requests
from urllib.parse import urlparse
from .base import BaseDownloader
from ..exceptions import NetworkError, ExtensionError

logger = logging.getLogger(__name__)


class ChromeDownloader(BaseDownloader):
    def extract_id(self, url):
        # Check if the input is already a valid ID (32 lowercase letters)
        if re.match(r"^[a-z]{32}$", url):
            return url

        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")

        if path_segments:
            possible_id = path_segments[-1]
            if re.match(r"^[a-z]{32}$", possible_id):
                return possible_id

        raise ExtensionError("Could not extract extension ID from Chrome Web Store URL")

    def get_latest_version(self, extension_id):
        # Using the update check XML API
        url = "https://clients2.google.com/service/update2/crx"
        params = {
            "x": f"id={extension_id}&uc",
            "prodversion": "131.0",
            "acceptformat": "crx2,crx3",
        }

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            # Simple regex to find version in XML response
            # <updatecheck codebase="..." version="1.2.3" />
            match = re.search(r'version="([0-9.]+)"', response.text)
            if match:
                return match.group(1)
            return None
        except requests.RequestException as e:
            logger.warning(f"Failed to check version for {extension_id}: {e}")
            return None

    def download(self, extension_id, output_dir, show_progress=True):
        download_url = (
            f"https://clients2.google.com/service/update2/crx"
            f"?response=redirect&prodversion=131.0&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc"
        )

        logger.info(f"Downloading Chrome extension {extension_id}...")

        output_path = output_dir / f"{extension_id}.crx"

        try:
            return self.client.download_file(
                download_url, output_path, show_progress=show_progress
            )

        except requests.RequestException as e:
            logger.error(f"Failed to download extension: {e}")
            raise NetworkError(
                f"Failed to download extension: {e}", original_exception=e
            )
