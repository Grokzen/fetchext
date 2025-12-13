import logging
from pathlib import Path
from typing import List, Dict, Any
from zipfile import ZipFile
from fetchext.crx import CrxDecoder

logger = logging.getLogger(__name__)


class YaraScanner:
    def __init__(self, rules_path: Path):
        try:
            import yara
        except ImportError:
            raise ImportError("yara-python is not installed. Install with 'pip install fetchext[security]'")
        
        self.rules_path = rules_path
        if not self.rules_path.exists():
            raise FileNotFoundError(f"YARA rules file not found: {rules_path}")

        try:
            if self.rules_path.is_dir():
                filepaths = {}
                # Find .yar and .yara files recursively
                rule_files = list(self.rules_path.glob("**/*.yar")) + list(self.rules_path.glob("**/*.yara"))
                
                for rule_file in rule_files:
                    # Use filename as namespace to avoid collisions if possible, 
                    # but simple stem is usually enough for display.
                    # To be safe against duplicates in different dirs, we could use the full path hash or similar,
                    # but let's stick to stem for readability in results.
                    filepaths[rule_file.stem] = str(rule_file)
                
                if not filepaths:
                    raise FileNotFoundError(f"No .yar or .yara files found in directory: {rules_path}")
                
                self.rules = yara.compile(filepaths=filepaths)
            else:
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

import logging
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any
from zipfile import ZipFile
from fetchext.crx import CrxDecoder

logger = logging.getLogger(__name__)


class YaraScanner:
    def __init__(self, rules_path: Path):
        try:
            import yara
        except ImportError:
            raise ImportError("yara-python is not installed. Install with 'pip install fetchext[security]'")
        
        self.rules_path = rules_path
        if not self.rules_path.exists():
            raise FileNotFoundError(f"YARA rules file not found: {rules_path}")

        try:
            if self.rules_path.is_dir():
                filepaths = {}
                # Find .yar and .yara files recursively
                rule_files = list(self.rules_path.glob("**/*.yar")) + list(self.rules_path.glob("**/*.yara"))
                
                for rule_file in rule_files:
                    # Use filename as namespace to avoid collisions if possible, 
                    # but simple stem is usually enough for display.
                    # To be safe against duplicates in different dirs, we could use the full path hash or similar,
                    # but let's stick to stem for readability in results.
                    filepaths[rule_file.stem] = str(rule_file)
                
                if not filepaths:
                    raise FileNotFoundError(f"No .yar or .yara files found in directory: {rules_path}")
                
                self.rules = yara.compile(filepaths=filepaths)
            else:
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
                    
                    # Memory optimization: For large files (>10MB), extract to temp file
                    # instead of reading into memory.
                    if info.file_size > 10 * 1024 * 1024:  # 10MB
                        with tempfile.NamedTemporaryFile(delete=False) as tmp:
                            try:
                                # Stream copy from zip to temp file
                                with zf.open(info.filename) as source:
                                    while True:
                                        chunk = source.read(8192)
                                        if not chunk:
                                            break
                                        tmp.write(chunk)
                                tmp.close()
                                
                                # Scan file on disk
                                matches = self.scan_file(Path(tmp.name))
                                # Fix filename in matches
                                for m in matches:
                                    m["filename"] = info.filename
                                
                                if matches:
                                    results[info.filename] = matches
                            finally:
                                os.unlink(tmp.name)
                    else:
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
