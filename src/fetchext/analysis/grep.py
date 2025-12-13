import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from ..utils import open_extension_archive

class GrepSearcher:
    def __init__(self, pattern: str, ignore_case: bool = False):
        flags = re.IGNORECASE if ignore_case else 0
        self.pattern = re.compile(pattern.encode('utf-8'), flags) # Search bytes

    def search_file(self, file_path: Path):
        results = []
        try:
            if file_path.is_dir():
                return []
            
            # Check if archive
            if file_path.suffix in ['.crx', '.xpi', '.zip']:
                results.extend(self._search_archive(file_path))
            else:
                # Regular file
                results.extend(self._search_text_file(file_path))
        except Exception:
            pass
        return results

    def _search_text_file(self, path: Path):
        matches = []
        try:
            with open(path, 'rb') as f:
                for i, line in enumerate(f, 1):
                    if self.pattern.search(line):
                        try:
                            decoded = line.decode('utf-8').strip()
                            # Truncate long lines
                            if len(decoded) > 200:
                                decoded = decoded[:200] + "..."
                            matches.append({
                                "file": str(path),
                                "line": i,
                                "content": decoded
                            })
                        except UnicodeDecodeError:
                            pass # Skip binary lines
        except Exception:
            pass
        return matches

    def _search_archive(self, path: Path):
        matches = []
        try:
            with open_extension_archive(path) as zf:
                for name in zf.namelist():
                    if name.endswith('/'):
                        continue
                    
                    try:
                        with zf.open(name) as f:
                            for i, line in enumerate(f, 1):
                                if self.pattern.search(line):
                                    try:
                                        decoded = line.decode('utf-8').strip()
                                        if len(decoded) > 200:
                                            decoded = decoded[:200] + "..."
                                        matches.append({
                                            "file": f"{path.name}:{name}",
                                            "line": i,
                                            "content": decoded
                                        })
                                    except UnicodeDecodeError:
                                        pass
                    except Exception:
                        pass
        except Exception:
            pass
        return matches

def search_directory(directory: Path, pattern: str, ignore_case: bool = False, max_workers: int = 4):
    searcher = GrepSearcher(pattern, ignore_case)
    results = []
    
    # Only scan files, skip .git and other hidden dirs
    files = [
        p for p in directory.rglob("*") 
        if p.is_file() and not any(part.startswith('.') for part in p.parts)
    ]
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(searcher.search_file, f): f for f in files}
        
        for future in as_completed(futures):
            try:
                res = future.result()
                if res:
                    results.extend(res)
            except Exception:
                pass
                
    return results
