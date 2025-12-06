import logging
from pathlib import Path
from typing import List, Dict, Any
from zipfile import ZipFile
from fetchext.crx import CrxDecoder

logger = logging.getLogger(__name__)

try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

class YaraScanner:
    def __init__(self, rules_path: Path):
        if not YARA_AVAILABLE:
            raise ImportError("yara-python is not installed. Install with 'pip install fetchext[security]'")
        
        self.rules_path = rules_path
        if not self.rules_path.exists():
            raise FileNotFoundError(f"YARA rules file not found: {rules_path}")

        try:
            self.rules = yara.compile(filepath=str(rules_path))
        except yara.Error as e:
            logger.error(f"Failed to compile YARA rules: {e}")
            raise

    def scan_content(self, content: bytes, filename: str = "") -> List[Dict[str, Any]]:
        """Scan bytes content against compiled rules."""
        matches = []
        try:
            yara_matches = self.rules.match(data=content)
            for match in yara_matches:
                matches.append({
                    "rule": match.rule,
                    "tags": match.tags,
                    "meta": match.meta,
                    "strings": match.strings,
                    "filename": filename
                })
        except Exception as e:
            logger.error(f"Error scanning content for {filename}: {e}")
        
        return matches

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a file on disk."""
        try:
            yara_matches = self.rules.match(filepath=str(file_path))
            matches = []
            for match in yara_matches:
                matches.append({
                    "rule": match.rule,
                    "tags": match.tags,
                    "meta": match.meta,
                    "strings": match.strings,
                    "filename": str(file_path)
                })
            return matches
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return []

    def scan_archive(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Scan all files within a CRX/XPI/ZIP archive."""
        results = {}
        
        f = None
        try:
            # Determine offset
            offset = 0
            if file_path.suffix.lower() == '.crx':
                offset = CrxDecoder.get_zip_offset(file_path)
                
            f = open(file_path, "rb")
            if offset > 0:
                f.seek(offset)
                
            try:
                zf = ZipFile(f)
            except Exception:
                # Try fallback if detection failed or wasn't tried
                if offset == 0:
                    f.seek(0)
                    # Check if it's a CRX despite extension
                    try:
                        offset = CrxDecoder.get_zip_offset(file_path)
                    except Exception:
                        offset = 0
                    
                    if offset > 0:
                        f.seek(offset)
                        zf = ZipFile(f)
                    else:
                        f.seek(0)
                        zf = ZipFile(f)
                else:
                    raise

            with zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    
                    # Read file content
                    content = zf.read(info.filename)
                    
                    # Scan content
                    matches = self.scan_content(content, filename=info.filename)
                    
                    if matches:
                        results[info.filename] = matches

        except Exception as e:
            logger.error(f"Error scanning archive {file_path}: {e}")
            raise
        finally:
            if f and not f.closed:
                f.close()
                
        return results
