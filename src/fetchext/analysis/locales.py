import zipfile
import json
from pathlib import Path
from typing import Dict, Any
from ..crx import CrxDecoder


def inspect_locales(file_path: Path) -> Dict[str, Any]:
    """
    Inspects the _locales directory of an extension.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    offset = 0
    try:
        offset = CrxDecoder.get_zip_offset(file_path)
    except Exception:
        pass

    locales = {}
    default_locale = None

    with open(file_path, "rb") as f:
        f.seek(offset)
        try:
            with zipfile.ZipFile(f) as zf:
                # Check manifest for default_locale
                try:
                    with zf.open("manifest.json") as mf:
                        manifest = json.load(mf)
                        default_locale = manifest.get("default_locale")
                except (KeyError, json.JSONDecodeError):
                    pass

                # Scan _locales directory
                for name in zf.namelist():
                    if name.startswith("_locales/") and name.endswith("messages.json"):
                        # Path format: _locales/<locale_code>/messages.json
                        parts = name.split("/")
                        if len(parts) >= 3:
                            locale_code = parts[1]
                            try:
                                with zf.open(name) as msg_file:
                                    messages = json.load(msg_file)
                                    locales[locale_code] = {
                                        "message_count": len(messages),
                                        "path": name,
                                    }
                            except (json.JSONDecodeError, Exception):
                                locales[locale_code] = {
                                    "message_count": 0,
                                    "error": "Failed to parse messages.json",
                                    "path": name,
                                }
        except zipfile.BadZipFile:
            raise ValueError("Invalid zip/crx file")

    return {
        "default_locale": default_locale,
        "supported_locales": list(locales.keys()),
        "details": locales,
    }
