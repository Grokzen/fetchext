import re
import logging
import requests
from urllib.parse import urlparse
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, TransferSpeedColumn
from ..console import console
from ..network import get_session
from .base import BaseDownloader
from ..exceptions import NetworkError, ExtensionError

logger = logging.getLogger(__name__)

class EdgeDownloader(BaseDownloader):
    def extract_id(self, url):
        # Check if the input is already a valid ID (32 lowercase letters)
        if re.match(r"^[a-z]{32}$", url):
            return url

        # Example: https://microsoftedge.microsoft.com/addons/detail/ublock-origin/odfafepnkmbhccpbejgmiehpchacaeak
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")

        if path_segments:
            possible_id = path_segments[-1]
            # Edge IDs are also 32 chars alphabetic
            if re.match(r"^[a-z]{32}$", possible_id):
                return possible_id

        raise ExtensionError("Could not extract extension ID from Edge Add-ons URL")

    def get_latest_version(self, extension_id):
        # Edge update URL
        url = "https://edge.microsoft.com/extensionwebstorebase/v1/crx"
        params = {
            "x": f"id={extension_id}&installsource=ondemand&uc",
            "prod": "chromiumcrx",
            "prodchannel": ""
        }
        
        try:
            with get_session() as session:
                response = session.get(url, params=params)
                response.raise_for_status()
                # Simple regex to find version in XML response
                match = re.search(r'version="([0-9.]+)"', response.text)
                if match:
                    return match.group(1)
                return None
        except requests.RequestException as e:
            logger.warning(f"Failed to check version for {extension_id}: {e}")
            return None

    def download(self, extension_id, output_dir, show_progress=True):
        # Edge uses a similar update protocol to Chrome
        download_url = (
            f"https://edge.microsoft.com/extensionwebstorebase/v1/crx"
            f"?response=redirect&prod=chromiumcrx&prodchannel=&x=id%3D{extension_id}%26installsource%3Dondemand%26uc"
        )

        logger.info(f"Downloading Edge extension {extension_id}...")

        try:
            with get_session() as session:
                response = session.get(download_url, stream=True)
                response.raise_for_status()

                filename = f"{extension_id}.crx"
            if "content-disposition" in response.headers:
                cd = response.headers["content-disposition"]
                filenames = re.findall('filename="(.+)"', cd)
                if filenames:
                    filename = filenames[0]

            output_path = output_dir / filename
            total_size = int(response.headers.get('content-length', 0))

            with output_path.open("wb") as f:
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
                        task = progress.add_task(filename, total=total_size)
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

            logger.info(f"Successfully downloaded to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Failed to download extension: {e}")
            raise NetworkError(f"Failed to download extension: {e}", original_exception=e)
