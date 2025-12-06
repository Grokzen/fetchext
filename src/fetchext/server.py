import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
from .inspector import ExtensionInspector
from .crx import CrxDecoder

logger = logging.getLogger(__name__)

def generate_update_manifest(directory: Path, base_url: str, output_file: Optional[Path] = None):
    """
    Generates an update manifest for extensions in the given directory.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
        
    base_url = base_url.rstrip("/")
    
    extensions = []
    inspector = ExtensionInspector()
    
    # Scan for files
    for file_path in directory.iterdir():
        if file_path.suffix not in [".crx", ".xpi"]:
            continue
            
        try:
            # Get Version from manifest
            manifest = inspector.get_manifest(file_path)
            version = manifest.get("version")
            if not version:
                logger.warning(f"Skipping {file_path.name}: No version in manifest")
                continue
                
            # Get ID
            ext_id = None
            if file_path.suffix == ".crx":
                try:
                    ext_id = CrxDecoder.get_id(file_path)
                except Exception as e:
                    logger.warning(f"Could not extract ID from CRX {file_path.name}: {e}")
            
            # Fallback ID from manifest (common for Firefox)
            if not ext_id:
                bss = manifest.get("browser_specific_settings", {}).get("gecko", {})
                ext_id = bss.get("id")
                
            if not ext_id:
                # Fallback to filename if it looks like an ID
                if len(file_path.stem) == 32:
                    ext_id = file_path.stem
                elif "@" in file_path.stem: # Firefox ID style
                    ext_id = file_path.stem
            
            if not ext_id:
                logger.warning(f"Skipping {file_path.name}: Could not determine Extension ID")
                continue
                
            extensions.append({
                "id": ext_id,
                "version": version,
                "file": file_path.name,
                "type": "crx" if file_path.suffix == ".crx" else "xpi"
            })
            
        except Exception as e:
            logger.warning(f"Error processing {file_path.name}: {e}")
            
    if not extensions:
        logger.warning("No valid extensions found.")
        return

    crx_extensions = [e for e in extensions if e["type"] == "crx"]
    xpi_extensions = [e for e in extensions if e["type"] == "xpi"]
    
    if crx_extensions:
        xml_content = _generate_chrome_xml(crx_extensions, base_url)
        out_path = output_file if output_file and output_file.suffix == ".xml" else directory / "update.xml"
        with open(out_path, "w") as f:
            f.write(xml_content)
        logger.info(f"Generated Chrome update manifest: {out_path}")
        
    if xpi_extensions:
        json_content = _generate_firefox_json(xpi_extensions, base_url)
        out_path = output_file if output_file and output_file.suffix == ".json" else directory / "updates.json"
        with open(out_path, "w") as f:
            f.write(json_content)
        logger.info(f"Generated Firefox update manifest: {out_path}")

def _generate_chrome_xml(extensions: List[Dict], base_url: str) -> str:
    """
    Generates Chrome Update Manifest XML (v3).
    """
    root = ET.Element("gupdate", xmlns="http://www.google.com/update2/response", protocol="2.0")
    
    for ext in extensions:
        app = ET.SubElement(root, "app", appid=ext["id"])
        ET.SubElement(app, "updatecheck", codebase=f"{base_url}/{ext['file']}", version=ext["version"])
        
    # Pretty print hack
    from xml.dom import minidom
    xml_str = ET.tostring(root, encoding="utf-8")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")

def _generate_firefox_json(extensions: List[Dict], base_url: str) -> str:
    """
    Generates Firefox Update Manifest JSON.
    """
    addons = {}
    
    for ext in extensions:
        addons[ext["id"]] = {
            "updates": [
                {
                    "version": ext["version"],
                    "update_link": f"{base_url}/{ext['file']}"
                }
            ]
        }
        
    return json.dumps({"addons": addons}, indent=2)
