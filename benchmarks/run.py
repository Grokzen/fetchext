import timeit
import tempfile
import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from fetchext.crx import CrxDecoder
from fetchext.analysis.entropy import calculate_shannon_entropy
from fetchext.analysis.complexity import _analyze_file_content
from fetchext.secrets import SecretScanner

console = Console()

def setup_crx(size_mb=1):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    # Write fake CRX header
    tmp.write(b'Cr24')
    tmp.write(b'\x03\x00\x00\x00') # Version 3
    tmp.write(b'\x00\x00\x00\x00') # Header len 0 (invalid but fast for parsing check)
    tmp.write(os.urandom(size_mb * 1024 * 1024))
    tmp.close()
    return Path(tmp.name)

def setup_js_file(lines=1000):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w")
    for i in range(lines):
        tmp.write(f"function func_{i}() {{ return {i} * {i}; }}\n")
        if i % 10 == 0:
            tmp.write("if (true) { console.log('nested'); }\n")
    tmp.close()
    return Path(tmp.name)

def setup_random_file(size_kb=100):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(os.urandom(size_kb * 1024))
    tmp.close()
    return Path(tmp.name)

def run_benchmarks():
    table = Table(title="Performance Benchmarks")
    table.add_column("Benchmark", style="cyan")
    table.add_column("Iterations", justify="right")
    table.add_column("Time (avg)", justify="right")
    table.add_column("Ops/sec", justify="right")

    benchmarks = []

    # 1. CRX Parsing (10MB)
    crx_path = setup_crx(10)
    def bench_crx():
        CrxDecoder.get_zip_offset(crx_path)
    
    benchmarks.append(("CRX Parse (10MB)", bench_crx, 100))

    # 2. Entropy (1MB)
    entropy_file = setup_random_file(1024)
    content = entropy_file.read_bytes()
    def bench_entropy():
        calculate_shannon_entropy(content)
    
    benchmarks.append(("Entropy (1MB)", bench_entropy, 50))

    # 3. Complexity (5000 lines JS)
    js_file = setup_js_file(5000)
    js_content = js_file.read_text()
    def bench_complexity():
        _analyze_file_content("test.js", js_content)
    
    benchmarks.append(("Complexity (5k lines JS)", bench_complexity, 20))

    # 4. Secret Scanning (1MB random)
    scanner = SecretScanner()
    # Convert bytes to string for regex scanning
    content_str = content.decode("utf-8", errors="ignore")
    lines = content_str.splitlines()
    
    def bench_secrets():
        for i, line in enumerate(lines):
            scanner._scan_line(line, "random.bin", i)
    
    benchmarks.append(("Secret Scan (1MB)", bench_secrets, 20))

    # Run them
    for name, func, iterations in benchmarks:
        console.print(f"Running {name}...", end="\r")
        total_time = timeit.timeit(func, number=iterations)
        avg_time = total_time / iterations
        ops_sec = 1.0 / avg_time
        
        table.add_row(
            name,
            str(iterations),
            f"{avg_time*1000:.2f} ms",
            f"{ops_sec:.2f}"
        )

    console.print(table)

    # Cleanup
    os.unlink(crx_path)
    os.unlink(entropy_file)
    os.unlink(js_file)

if __name__ == "__main__":
    run_benchmarks()
