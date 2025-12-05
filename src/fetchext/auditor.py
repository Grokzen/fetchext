import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from .utils import open_extension_archive

@dataclass
class AuditIssue:
    severity: str  # "error", "warning", "info"
    message: str
    file: str = "manifest.json"
    line: Optional[int] = None

@dataclass
class AuditReport:
    manifest_version: int
    issues: List[AuditIssue] = field(default_factory=list)
    
    @property
    def is_mv3(self):
        return self.manifest_version == 3

class ExtensionAuditor:
    def audit(self, file_path: Path) -> AuditReport:
        with open_extension_archive(file_path) as zf:
            # Read manifest
            try:
                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)
            except KeyError:
                return AuditReport(0, [AuditIssue("error", "manifest.json not found")])
            except json.JSONDecodeError:
                return AuditReport(0, [AuditIssue("error", "manifest.json is invalid JSON")])
                
            report = AuditReport(manifest_version=manifest.get("manifest_version", 0))
            
            self._check_manifest(manifest, report)
            self._scan_code(zf, report)
            
            return report
            
    def _check_manifest(self, manifest: Dict[str, Any], report: AuditReport):
        mv = report.manifest_version
        if mv == 2:
            report.issues.append(AuditIssue("warning", "Extension is using Manifest V2, which is deprecated."))
        elif mv == 3:
            report.issues.append(AuditIssue("info", "Extension is using Manifest V3."))
        else:
            report.issues.append(AuditIssue("error", f"Unknown manifest version: {mv}"))
            
        # Check for deprecated keys in MV3 context
        # Even if it is MV2, we warn about migration
        
        if "browser_action" in manifest:
            report.issues.append(AuditIssue("warning", "'browser_action' is deprecated in MV3. Use 'action' instead."))
            
        if "page_action" in manifest:
            report.issues.append(AuditIssue("warning", "'page_action' is deprecated in MV3. Use 'action' instead."))
            
        if "background" in manifest:
            bg = manifest["background"]
            if "scripts" in bg:
                report.issues.append(AuditIssue("warning", "Persistent background pages ('background.scripts') are replaced by Service Workers in MV3."))
            if "persistent" in bg and bg["persistent"]:
                 report.issues.append(AuditIssue("warning", "Persistent background pages are not supported in MV3."))

    def _scan_code(self, zf, report: AuditReport):
        # Simple regex scan for JS files
        js_files = [f for f in zf.namelist() if f.endswith(".js")]
        
        patterns = [
            (r"chrome\.browserAction", "warning", "chrome.browserAction is deprecated in MV3. Use chrome.action."),
            (r"chrome\.pageAction", "warning", "chrome.pageAction is deprecated in MV3. Use chrome.action."),
            (r"chrome\.webRequest", "info", "chrome.webRequest blocking is limited in MV3. Consider declarativeNetRequest."),
        ]
        
        for filename in js_files:
            try:
                # Limit read size to avoid memory issues with massive JS files?
                # For now, read full.
                content = zf.read(filename).decode("utf-8", errors="ignore")
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    for pattern, severity, msg in patterns:
                        if re.search(pattern, line):
                            report.issues.append(AuditIssue(severity, msg, filename, i + 1))
            except Exception:
                pass # Ignore read errors
