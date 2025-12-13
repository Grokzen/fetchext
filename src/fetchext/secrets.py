import re
import math
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

    # Known false positives for generic matches
    FALSE_POSITIVES = {
        "YOUR_API_KEY", "YOUR_TOKEN", "REPLACE_ME", "EXAMPLE_KEY",
        "API_KEY_HERE", "INSERT_KEY_HERE", "TEST_TOKEN", "SAMPLE_KEY",
        "undefined", "null", "true", "false", "string", "number",
        "object", "function", "boolean", "symbol", "bigint"
    }

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
                    # Use streaming to avoid loading entire file into memory
                    with zf.open(filename) as f:
                        for i, line_bytes in enumerate(f):
                            try:
                                line = line_bytes.decode("utf-8", errors="ignore")
                                findings.extend(self._scan_line(line, filename, i + 1))
                            except Exception:
                                pass
                except Exception:
                    pass # Ignore read errors
        return findings

    def _calculate_entropy(self, s: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not s:
            return 0.0
        
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

    def _scan_line(self, line: str, filename: str, line_number: int) -> List[SecretFinding]:
        findings = []
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
            
            full_match = match.group(0)
            
            # False Positive Reduction for Generic API Key
            if name == "Generic API Key":
                secret_value = match.group(2)
                
                # 1. Check against known false positives
                if any(fp in secret_value.upper() for fp in self.FALSE_POSITIVES):
                    continue
                    
                # 2. Check entropy (randomness)
                # A real API key usually has high entropy (> 3.0 for ~20 chars)
                # Simple words or repeated chars have low entropy.
                entropy = self._calculate_entropy(secret_value)
                if entropy < 3.0:
                    continue
                    
                # 3. Check if it looks like a URL or path
                if secret_value.startswith(("http", "//", "/", "./", "../")):
                    continue

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
            
            matched_ranges.add((start, end))
            findings.append(SecretFinding(
                type=name,
                file=filename,
                line=line_number,
                match=masked
            ))
        return findings
