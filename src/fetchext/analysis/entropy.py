import math
from pathlib import Path
from typing import Dict, List, Union
from zipfile import ZipFile
from fetchext.crx import CrxDecoder

def calculate_shannon_entropy(data: bytes) -> float:
    """
    Calculate the Shannon entropy of a byte sequence.
    Returns a value between 0 and 8.
    """
    if not data:
        return 0.0
    
    entropy = 0
    length = len(data)
    counts = [0] * 256
    
    for byte in data:
        counts[byte] += 1
        
    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
            
    return entropy

def analyze_entropy(file_path: Path) -> Dict[str, Union[float, List[Dict[str, Union[str, float]]]]]:
    """
    Analyze the entropy of files within an extension.
    
    Returns:
        Dict containing average entropy and a list of file details.
    """
    results = {
        "average_entropy": 0.0,
        "files": []
    }
    
    total_entropy = 0.0
    file_count = 0
    
    try:
        # Determine offset
        offset = 0
        if file_path.suffix.lower() == '.crx':
            offset = CrxDecoder.get_zip_offset(file_path)
            
        # Open as ZipFile
        # If offset > 0, we need to handle it.
        # Python's ZipFile takes a file object.
        
        f = open(file_path, "rb")
        if offset > 0:
            f.seek(offset)
            
        try:
            zf = ZipFile(f)
        except Exception:
            f.close()
            # If it failed and we didn't try offset (e.g. .zip file that is actually a CRX), try detecting CRX
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
        
        # Now iterate
        with zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                
                data = zf.read(info.filename)
                entropy = calculate_shannon_entropy(data)
                
                results["files"].append({
                    "filename": info.filename,
                    "entropy": entropy,
                    "size": info.file_size
                })
                
                total_entropy += entropy
                file_count += 1
                
        if file_count > 0:
            results["average_entropy"] = total_entropy / file_count
            
    except Exception as e:
        raise ValueError(f"Error analyzing entropy: {e}")
    finally:
        # f is closed by zf context manager if zf was created successfully?
        # No, ZipFile(f) does not close f automatically unless we use it in a with block?
        # Actually, ZipFile context manager closes the file if it opened it, or if we passed a filename.
        # If we passed a file object, ZipFile does NOT close it by default in older python, but in 3.11 it might.
        # To be safe, we should ensure f is closed if zf didn't take ownership or if we are done.
        # But since we used `with zf:`, zf.close() is called.
        # Does zf.close() close the underlying file object?
        # Documentation says: "If the file was opened by passing a file name, it is closed. If a file object was passed, it is NOT closed."
        # So we need to close f.
        if 'f' in locals() and not f.closed:
            f.close()

    return results

    return results
