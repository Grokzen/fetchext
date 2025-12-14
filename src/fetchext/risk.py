import json
from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from .utils import open_extension_archive


@dataclass
class PermissionRisk:
    permission: str
    score: int
    level: str  # Critical, High, Medium, Low
    description: str


@dataclass
class RiskReport:
    total_score: int
    max_level: str
    risky_permissions: List[PermissionRisk] = field(default_factory=list)
    safe_permissions: List[str] = field(default_factory=list)


class RiskAnalyzer:
    # Define risk database
    RISK_DB = {
        # Critical
        "<all_urls>": (10, "Access to all data on all websites"),
        "debugger": (10, "Debug and inspect pages"),
        "proxy": (10, "Control proxy settings"),
        "webRequestBlocking": (10, "Intercept and block network requests"),
        "cookies": (9, "Read and modify cookies"),
        "pageCapture": (9, "Capture page content"),
        "declarativeNetRequest": (8, "Block or modify network requests (MV3)"),
        "scripting": (8, "Execute scripts on pages"),
        # High
        "tabs": (7, "Access browser tabs and navigation"),
        "activeTab": (6, "Access content of the active tab"),
        "history": (7, "Read and modify browsing history"),
        "bookmarks": (7, "Read and modify bookmarks"),
        "management": (7, "Manage other extensions"),
        "privacy": (7, "Change privacy settings"),
        "topSites": (7, "Access most visited sites"),
        "webNavigation": (7, "Monitor navigation events"),
        "clipboardRead": (6, "Read data from clipboard"),
        "clipboardWrite": (5, "Write data to clipboard"),
        # Medium
        "storage": (4, "Store data locally"),
        "unlimitedStorage": (4, "Store unlimited data"),
        "notifications": (4, "Show notifications"),
        "contextMenus": (4, "Add items to context menu"),
        "downloads": (5, "Manage downloads"),
        "geolocation": (5, "Access location"),
        "webRequest": (5, "Observe network requests"),
        # Low
        "alarms": (1, "Schedule alarms"),
        "idle": (1, "Detect idle state"),
        "power": (1, "Manage power settings"),
        "printerProvider": (1, "Access printers"),
    }

    # Toxic combinations that amplify risk
    RISK_COMBINATIONS = [
        (
            {"tabs", "cookies", "<all_urls_normalized>"},
            20,
            "Critical",
            "Session Hijacking Risk (Tabs + Cookies + All URLs)",
        ),
        (
            {"webRequest", "webRequestBlocking", "<all_urls_normalized>"},
            20,
            "Critical",
            "Man-in-the-Middle Risk (Intercept + Block + All URLs)",
        ),
        (
            {"declarativeNetRequest", "<all_urls_normalized>"},
            15,
            "Critical",
            "Ad Injection / Traffic Modification Risk",
        ),
        (
            {"scripting", "<all_urls_normalized>"},
            15,
            "Critical",
            "Arbitrary Code Execution on All Pages",
        ),
        (
            {"clipboardRead", "clipboardWrite"},
            10,
            "High",
            "Full Clipboard Access (Read + Write)",
        ),
        ({"history", "tabs"}, 10, "High", "Comprehensive Browsing Activity Tracking"),
    ]

    def analyze(self, file_path: Path) -> RiskReport:
        with open_extension_archive(file_path) as zf:
            try:
                manifest = json.loads(zf.read("manifest.json"))
            except Exception:
                return RiskReport(0, "Unknown")

            permissions = manifest.get("permissions", [])
            # Also check host permissions in MV3
            host_permissions = manifest.get("host_permissions", [])
            all_perms = set(permissions + host_permissions)

            risky_perms = []
            safe_perms = []
            total_score = 0

            # Normalize permissions for combination checking
            normalized_perms = set(all_perms)
            for perm in all_perms:
                if perm == "<all_urls>" or "*://*/*" in perm or "https://*/*" in perm:
                    normalized_perms.add("<all_urls_normalized>")

            for perm in all_perms:
                # Check for host patterns (e.g. *://*/*)
                if "://" in perm or perm == "<all_urls>":
                    if perm == "<all_urls>" or "*://*/*" in perm:
                        score, desc = (10, "Access to all data on all websites")
                        level = "Critical"
                    elif "*://" in perm:
                        score, desc = (8, f"Access to data on {perm}")
                        level = "High"
                    else:
                        score, desc = (5, f"Access to data on {perm}")
                        level = "Medium"
                elif perm in self.RISK_DB:
                    score, desc = self.RISK_DB[perm]
                    if score >= 9:
                        level = "Critical"
                    elif score >= 6:
                        level = "High"
                    elif score >= 4:
                        level = "Medium"
                    else:
                        level = "Low"
                else:
                    score = 0
                    level = "Safe"
                    desc = "Unknown or safe permission"

                if score > 0:
                    total_score += score
                    risky_perms.append(PermissionRisk(perm, score, level, desc))
                else:
                    safe_perms.append(perm)

            # Check for toxic combinations
            for req_perms, bonus_score, level, desc in self.RISK_COMBINATIONS:
                if req_perms.issubset(normalized_perms):
                    total_score += bonus_score
                    risky_perms.append(
                        PermissionRisk("COMBINATION", bonus_score, level, desc)
                    )

            # Determine max level
            max_level = "Safe"
            if any(p.level == "Critical" for p in risky_perms):
                max_level = "Critical"
            elif any(p.level == "High" for p in risky_perms):
                max_level = "High"
            elif any(p.level == "Medium" for p in risky_perms):
                max_level = "Medium"
            elif any(p.level == "Low" for p in risky_perms):
                max_level = "Low"

            # Sort risky permissions by score descending
            risky_perms.sort(key=lambda x: x.score, reverse=True)

            return RiskReport(total_score, max_level, risky_perms, safe_perms)
