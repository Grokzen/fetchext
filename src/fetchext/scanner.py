import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from .utils import open_extension_archive

logger = logging.getLogger(__name__)


@dataclass
class DetectedLibrary:
    name: str
    version: str
    path: str
    vulnerable: bool = False
    advisory: Optional[str] = None


@dataclass
class ScanReport:
    file: str
    libraries: List[DetectedLibrary] = field(default_factory=list)


class DependencyScanner:
    # Regex patterns to detect libraries in file content (header comments)
    SIGNATURES = [
        (r"jQuery v([0-9.]+)", "jquery"),
        (r"React v([0-9.]+)", "react"),
        (r"Vue\.js v([0-9.]+)", "vue"),
        (r"Lodash <([0-9.]+)>", "lodash"),
        (r"moment\.js ([0-9.]+)", "moment"),
        (r"AngularJS v([0-9.]+)", "angularjs"),
        (r"Bootstrap v([0-9.]+)", "bootstrap"),
    ]

    # Vulnerability rules (Name, Max Safe Version)
    # If version < Max Safe, it's vulnerable.
    VULNERABILITIES = {
        "jquery": ("3.5.0", "XSS vulnerabilities in < 3.5.0"),
        "lodash": ("4.17.21", "Prototype pollution in < 4.17.21"),
        "bootstrap": ("4.0.0", "XSS in < 4.0.0"),
        "moment": ("2.29.4", "ReDoS in < 2.29.4"),
        "angularjs": ("1.8.0", "XSS in < 1.8.0"),
    }

    def scan(self, file_path: Path) -> ScanReport:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        report = ScanReport(file=file_path.name)

        try:
            with open_extension_archive(file_path) as zf:
                for filename in zf.namelist():
                    if not filename.endswith(".js"):
                        continue

                    # Read first 1KB for header detection
                    with zf.open(filename) as f:
                        try:
                            head = f.read(1024).decode("utf-8", errors="ignore")
                            lib = self._detect_library(filename, head)
                            if lib:
                                lib.path = filename
                                report.libraries.append(lib)
                        except Exception:
                            continue
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise

        return report

    def _detect_library(
        self, filename: str, content_head: str
    ) -> Optional[DetectedLibrary]:
        # 1. Check content signatures
        for pattern, name in self.SIGNATURES:
            match = re.search(pattern, content_head, re.IGNORECASE)
            if match:
                version = match.group(1)
                return self._create_library(name, version, filename)

        # 2. Check filename (fallback)
        if "jquery" in filename.lower():
            # Match version number that ends with a digit (avoid trailing dot)
            match = re.search(r"jquery[-._]?([0-9.]+[0-9])", filename, re.IGNORECASE)
            if match:
                return self._create_library("jquery", match.group(1), filename)

        return None

    def _create_library(self, name: str, version: str, path: str) -> DetectedLibrary:
        vuln = False
        advisory = None

        if name in self.VULNERABILITIES:
            safe_ver, msg = self.VULNERABILITIES[name]
            if self._is_version_less(version, safe_ver):
                vuln = True
                advisory = msg

        return DetectedLibrary(
            name=name, version=version, path=path, vulnerable=vuln, advisory=advisory
        )

    def _is_version_less(self, v1: str, v2: str) -> bool:
        try:
            from packaging import version

            return version.parse(v1) < version.parse(v2)
        except ImportError:
            return v1 < v2
