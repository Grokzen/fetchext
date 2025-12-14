import re
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List
from ..utils import open_extension_archive

@dataclass
class RuleMatch:
    rule_id: str
    description: str
    severity: str
    file: str
    line: int
    match: str

class RuleEngine:
    def __init__(self, rules_path: Path = None):
        self.rules = []
        if rules_path:
            self.load_rules(rules_path)

    def load_rules(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Rules file not found: {path}")
            
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        if not data or "rules" not in data:
            raise ValueError("Invalid rules file format")
            
        for rule in data["rules"]:
            self.rules.append({
                "id": rule.get("id"),
                "description": rule.get("description", ""),
                "severity": rule.get("severity", "medium"),
                "pattern": re.compile(rule.get("pattern"), re.IGNORECASE)
            })

    def scan(self, file_path: Path) -> List[RuleMatch]:
        matches = []
        
        # Helper to scan content
        def scan_content(filename, content_lines):
            for i, line in enumerate(content_lines, 1):
                try:
                    line_str = line.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                    
                for rule in self.rules:
                    if rule["pattern"].search(line_str):
                        matches.append(RuleMatch(
                            rule_id=rule["id"],
                            description=rule["description"],
                            severity=rule["severity"],
                            file=filename,
                            line=i,
                            match=line_str.strip()[:100] # Truncate
                        ))

        if file_path.is_dir():
            for p in file_path.rglob("*"):
                if p.is_file():
                    try:
                        with open(p, "rb") as f:
                            scan_content(str(p.relative_to(file_path)), f)
                    except Exception:
                        pass
        else:
            # Archive
            try:
                with open_extension_archive(file_path) as zf:
                    for name in zf.namelist():
                        if name.endswith("/"):
                            continue
                        try:
                            with zf.open(name) as f:
                                scan_content(name, f)
                        except Exception:
                            pass
            except Exception:
                pass
            
        return matches
