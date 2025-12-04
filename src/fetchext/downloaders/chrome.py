import re
import logging
import requests
from urllib.parse import urlparse
from tqdm import tqdm
from .base import BaseDownloader

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

        raise ValueError("Could not extract extension ID from Chrome Web Store URL")

    def download(self, extension_id, output_dir, show_progress=True):
        download_url = (
            f"https://clients2.google.com/service/update2/crx"
            f"?response=redirect&prodversion=131.0&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc"
        )

        logger.info(f"Downloading Chrome extension {extension_id}...")

        try:
            response = requests.get(download_url, stream=True)
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
                    with tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                        leave=False
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            bar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            if not output_path.exists() or output_path.stat().st_size == 0:
                if output_path.exists():
                    output_path.unlink()
                raise RuntimeError("Download failed: File is empty or does not exist.")

            logger.info(f"Successfully downloaded to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Failed to download extension: {e}")
            raise
