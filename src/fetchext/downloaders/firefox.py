import logging
from pathlib import Path
from urllib.parse import urlparse
from .base import BaseDownloader
from fetchext.core.exceptions  import NetworkError, ExtensionError
from fetchext.utils  import sanitize_filename

logger = logging.getLogger(__name__)


class FirefoxDownloader(BaseDownloader):
    def extract_id(self, url):
        # Example: https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")

        # The slug is usually after 'addon'
        try:
            addon_index = path_segments.index("addon")
            if addon_index + 1 < len(path_segments):
                return path_segments[addon_index + 1]
        except ValueError:
            pass

        raise ExtensionError(
            "Could not extract extension slug from Firefox Add-ons URL"
        )

    def download(self, extension_id, output_dir, show_progress=True):
        # Use AMO API to get the download URL
        # extension_id here is the slug (e.g., 'ublock-origin')
        api_url = f"https://addons.mozilla.org/api/v5/addons/addon/{extension_id}/"

        logger.info(f"Fetching metadata for Firefox extension {extension_id}...")

        try:
            # Get metadata
            meta_response = self.client.get(api_url)
            meta_response.raise_for_status()
            data = meta_response.json()

            # Get the latest version file URL
            if "current_version" in data and "file" in data["current_version"]:
                download_url = data["current_version"]["file"]["url"]
                raw_filename = Path(urlparse(download_url).path).name
                filename = sanitize_filename(raw_filename)
            else:
                raise NetworkError("Could not find download URL in metadata")

            logger.info(f"Downloading from {download_url}...")

            output_path = output_dir / filename
            return self.client.download_file(
                download_url, output_path, show_progress=show_progress
            )

        except Exception as e:
            logger.error(f"Failed to download extension: {e}")
            raise NetworkError(
                f"Failed to download extension: {e}", original_exception=e
            )

    def get_latest_version(self, extension_id):
        api_url = f"https://addons.mozilla.org/api/v5/addons/addon/{extension_id}/"
        try:
            response = self.client.get(api_url)
            response.raise_for_status()
            data = response.json()
            if "current_version" in data:
                return data["current_version"]["version"]
            return None
        except Exception as e:
            logger.warning(f"Failed to check version for {extension_id}: {e}")
            return None

    def search(self, query):
        url = "https://addons.mozilla.org/api/v5/addons/search/"
        params = {"q": query, "app": "firefox", "type": "extension"}

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()

            return response.json().get("results", [])

        except Exception as e:
            logger.error(f"Failed to search for extension: {e}")
            raise NetworkError(
                f"Failed to search for extension: {e}", original_exception=e
            )
