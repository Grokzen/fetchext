import re
from dataclasses import dataclass
from typing import List
from pathlib import Path
from .utils import open_extension_archive

@dataclass
class SecretFinding:
    type: str
    file: str
    line: int
    match: str  # Masked

class SecretScanner:
    # Regex patterns for common secrets
    # Order matters! More specific patterns should come first.
    PATTERNS = [
        ("AWS Access Key", r"AKIA[0-9A-Z]{16}"),
        ("Google API Key", r"AIza[0-9A-Za-z\-_]{35}"),
        ("Slack Token", r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
        ("Stripe Secret Key", r"sk_live_[0-9a-zA-Z]{24}"),
        ("Private Key", r"-----BEGIN [A-Z]+ PRIVATE KEY-----"),
        # Generic API Key is very broad, so it should be last.
        ("Generic API Key", r"(?i)(api_key|apikey|secret|token)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]"),
    ]

    def scan_extension(self, file_path: Path) -> List[SecretFinding]:
        findings = []
        with open_extension_archive(file_path) as zf:
            for filename in zf.namelist():
                if filename.endswith(("/", "\\")):
                    continue
                
                # Skip binary files based on extension
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4", ".wav")):
                    continue

                try:
                    content = zf.read(filename).decode("utf-8", errors="ignore")
                    findings.extend(self._scan_content(content, filename))
                except Exception:
                    pass # Ignore read errors
        return findings

    def _scan_content(self, content: str, filename: str) -> List[SecretFinding]:
        findings = []
        lines = content.splitlines()
        for i, line in enumerate(lines):
            # Use a set to track matched ranges in this line to avoid overlapping matches
            matched_ranges = set()
            
            # Collect all matches first
            all_matches = []
            for name, pattern in self.PATTERNS:
                for match in re.finditer(pattern, line):
                    all_matches.append((name, match))
            
            # Prioritize specific types
            type_priority = {
                "AWS Access Key": 10,
                "Google API Key": 10,
                "Slack Token": 10,
                "Stripe Secret Key": 10,
                "Private Key": 10,
                "Generic API Key": 1
            }
            
            # Sort by priority (descending) then by start position
            all_matches.sort(key=lambda x: (-type_priority.get(x[0], 0), x[1].start()))
            
            for name, match in all_matches:
                start, end = match.span()
                
                # Check for overlap
                is_overlap = False
                for r_start, r_end in matched_ranges:
                    if (start < r_end and end > r_start):
                        is_overlap = True
                        break
                
                if is_overlap:
                    continue
                    
                matched_ranges.add((start, end))
                
                full_match = match.group(0)
                # If it's a Generic API Key, the group(2) is the actual secret
                if name == "Generic API Key":
                    # Re-implement masking to be simpler and consistent
                    if len(full_match) > 12:
                         masked = full_match[:8] + "*" * (len(full_match) - 12) + full_match[-4:]
                    else:
                         masked = "*" * len(full_match)
                else:
                    # Standard masking
                    if len(full_match) > 8:
                        masked = full_match[:4] + "*" * (len(full_match) - 4)
                    else:
                        masked = "*" * len(full_match)
                    
                findings.append(SecretFinding(
                    type=name,
                    file=filename,
                    line=i + 1,
                    match=masked
                ))
        return findings
