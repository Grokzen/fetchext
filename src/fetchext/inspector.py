import json
import logging
from .utils import open_extension_archive

logger = logging.getLogger(__name__)

class ExtensionInspector:
    def get_manifest(self, file_path):
        try:
            with open_extension_archive(file_path) as zf:
                if "manifest.json" not in zf.namelist():
                    raise ValueError("manifest.json not found in archive")

                with zf.open("manifest.json") as f:
                    return json.load(f)

        except Exception as e:
            logger.error(f"Failed to inspect file: {e}")
            raise ValueError("Could not parse file as extension archive") from e
