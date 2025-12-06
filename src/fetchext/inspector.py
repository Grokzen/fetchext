import json
import logging
from datetime import datetime
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

    def get_timeline(self, file_path):
        """
        Returns a sorted list of files in the archive with their modification times.
        """
        timeline = []
        try:
            with open_extension_archive(file_path) as zf:
                for info in zf.infolist():
                    # ZipInfo.date_time is a tuple (year, month, day, hour, min, sec)
                    dt_tuple = info.date_time
                    dt = datetime(*dt_tuple)
                    timeline.append({
                        "filename": info.filename,
                        "datetime": dt,
                        "size": info.file_size
                    })
            
            # Sort by datetime
            timeline.sort(key=lambda x: x["datetime"])
            return timeline

        except Exception as e:
            logger.error(f"Failed to generate timeline: {e}")
            raise ValueError("Could not read archive for timeline") from e
