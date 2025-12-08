import math
import concurrent.futures
import os
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

def _process_file_entropy(filename: str, data: bytes, size: int) -> Dict[str, Union[str, float, int]]:
    """Helper function to run in a separate process."""
    entropy = calculate_shannon_entropy(data)
    return {
        "filename": filename,
        "entropy": entropy,
        "size": size
    }

def analyze_entropy(file_path: Path) -> Dict[str, Union[float, List[Dict[str, Union[str, float]]]]]:
    """
    Analyze the entropy of files within an extension.
    Uses parallel processing for performance.
    
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
        f = open(file_path, "rb")
        if offset > 0:
            f.seek(offset)
            
        try:
            zf = ZipFile(f)
        except Exception:
            f.close()
            # Fallback logic
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
        
        # Use ProcessPoolExecutor for CPU-bound entropy calculation
        # We read files in the main thread (I/O bound) and send data to workers
        max_workers = os.cpu_count() or 4
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            with zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    
                    # Read data in main thread
                    data = zf.read(info.filename)
                    
                    # Submit to pool
                    futures.append(
                        executor.submit(_process_file_entropy, info.filename, data, info.file_size)
                    )
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    results["files"].append(res)
                    total_entropy += res["entropy"]
                    file_count += 1
                except Exception:
                    pass # Ignore failures for individual files

        if file_count > 0:
            results["average_entropy"] = total_entropy / file_count
            
    except Exception as e:
        raise ValueError(f"Error analyzing entropy: {e}")
    finally:
        if 'f' in locals() and not f.closed:
            f.close()

    return results
