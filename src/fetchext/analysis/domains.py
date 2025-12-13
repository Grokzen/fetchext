import re
from pathlib import Path
from typing import Dict, List, Set
from zipfile import ZipFile
from urllib.parse import urlparse
from fetchext.crx import CrxDecoder
from ..console import console

# Regex for finding URLs
# Matches http, https, ws, wss, ftp
URL_PATTERN = re.compile(r'(https?|wss?|ftp)://[^\s/$.?#].[^\s"\']*[^\s"\'.]')

def extract_domains_from_text(text: str) -> Dict[str, Set[str]]:
    """
    Extract URLs and domains from a string.
    """
    urls = set()
    domains = set()
    
    matches = URL_PATTERN.findall(text)
    for match in matches:
        # findall with groups returns the group, but we want the whole match if we didn't group the whole thing.
        # Actually, the regex above has a group (https?|...), so findall returns just the protocol if we are not careful.
        # Let's use finditer.
        pass

    for match in URL_PATTERN.finditer(text):
        url = match.group(0)
        urls.add(url)
        
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                domains.add(parsed.netloc)
        except Exception:
            pass
            
    return {"urls": urls, "domains": domains}

def analyze_domains(file_path: Path, show_progress: bool = True) -> Dict[str, List[str]]:
    """
    Analyze an extension file to extract domains and URLs.
    
    Returns:
        Dict with 'domains' and 'urls' lists (sorted).
    """
    all_urls = set()
    all_domains = set()
    
    target_extensions = {'.js', '.html', '.css', '.json', '.xml', '.txt'}
    
    try:
        # Determine offset for CRX
        offset = 0
        if file_path.suffix.lower() == '.crx':
            offset = CrxDecoder.get_zip_offset(file_path)
            
        f = open(file_path, "rb")
        if offset > 0:
            f.seek(offset)
            
        try:
            zf = ZipFile(f)
        except Exception:
            f.close()
            if offset == 0:
                offset = CrxDecoder.get_zip_offset(file_path)
                if offset > 0:
                    f = open(file_path, "rb")
                    f.seek(offset)
                    try:
                        zf = ZipFile(f)
                    except Exception:
                        f.close()
                        raise ValueError("Could not open file as ZIP or CRX")
                else:
                    raise ValueError("Could not open file as ZIP")
            else:
                raise ValueError("Could not open file as CRX")
        
        with zf:
            file_list = zf.infolist()
            
            if show_progress:
                with console.create_progress() as progress:
                    task = progress.add_task("Analyzing Domains", total=len(file_list))
                    for info in file_list:
                        if info.is_dir():
                            progress.advance(task)
                            continue
                        
                        ext = Path(info.filename).suffix.lower()
                        if ext in target_extensions:
                            try:
                                # Read and decode as text
                                content_bytes = zf.read(info.filename)
                                # Try UTF-8, fallback to Latin-1
                                try:
                                    text = content_bytes.decode('utf-8')
                                except UnicodeDecodeError:
                                    text = content_bytes.decode('latin-1')
                                    
                                extracted = extract_domains_from_text(text)
                                all_urls.update(extracted["urls"])
                                all_domains.update(extracted["domains"])
                            except Exception:
                                # Skip files that can't be read/decoded
                                pass
                        progress.advance(task)
            else:
                for info in file_list:
                    if info.is_dir():
                        continue
                    
                    ext = Path(info.filename).suffix.lower()
                    if ext in target_extensions:
                        try:
                            # Read and decode as text
                            content_bytes = zf.read(info.filename)
                            # Try UTF-8, fallback to Latin-1
                            try:
                                text = content_bytes.decode('utf-8')
                            except UnicodeDecodeError:
                                text = content_bytes.decode('latin-1')
                                
                            extracted = extract_domains_from_text(text)
                            all_urls.update(extracted["urls"])
                            all_domains.update(extracted["domains"])
                        except Exception:
                            # Skip files that can't be read/decoded
                            continue
        
        # Close file if needed (ZipFile context manager closes it if it owns it, but here we passed f)
        # See previous discussion: ZipFile(f) does not close f automatically in all versions.
        if 'f' in locals() and not f.closed:
            f.close()
            
    except Exception as e:
        raise ValueError(f"Error analyzing domains: {e}")

    return {
        "domains": sorted(list(all_domains)),
        "urls": sorted(list(all_urls))
    }
