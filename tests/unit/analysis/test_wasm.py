import pytest
from pathlib import Path
from fetchext.analysis.wasm import analyze_wasm

@pytest.fixture
def minimal_wasm(fs):
    path = Path("/tmp/minimal.wasm")
    # Magic + Version
    content = b'\x00asm\x01\x00\x00\x00'
    fs.create_file(path, contents=content)
    return path

@pytest.fixture
def complex_wasm(fs):
    path = Path("/tmp/complex.wasm")
    content = bytearray(b'\x00asm\x01\x00\x00\x00')
    
    # Type Section (ID 1): 1 type, func() -> ()
    # ID=1, Size=4, Count=1, Form=0x60, ParamCount=0, ResultCount=0
    content.extend(b'\x01\x04\x01\x60\x00\x00')
    
    # Import Section (ID 2): 1 import "env.log" (func type 0)
    # ID=2, Size=11, Count=1, ModLen=3, "env", FieldLen=3, "log", Kind=0, TypeIdx=0
    content.extend(b'\x02\x0b\x01\x03env\x03log\x00\x00')
    
    # Function Section (ID 3): 1 function (type 0)
    # ID=3, Size=2, Count=1, TypeIdx=0
    content.extend(b'\x03\x02\x01\x00')
    
    # Export Section (ID 7): 1 export "main" (func 0)
    # ID=7, Size=8, Count=1, NameLen=4, "main", Kind=0, FuncIdx=0
    content.extend(b'\x07\x08\x01\x04main\x00\x00')
    
    # Custom Section (ID 0): "name"
    # ID=0, Size=5, NameLen=4, "name"
    content.extend(b'\x00\x05\x04name')

    fs.create_file(path, contents=content)
    return path

def test_analyze_minimal_wasm(minimal_wasm):
    stats = analyze_wasm(minimal_wasm)
    assert stats["version"] == 1
    assert stats["size"] == 8
    assert len(stats["sections"]) == 0

def test_analyze_complex_wasm(complex_wasm):
    stats = analyze_wasm(complex_wasm)
    assert stats["version"] == 1
    assert stats["functions_count"] == 1
    
    # Check sections
    section_ids = [s["id"] for s in stats["sections"]]
    assert 1 in section_ids # Type
    assert 2 in section_ids # Import
    assert 3 in section_ids # Function
    assert 7 in section_ids # Export
    assert 0 in section_ids # Custom
    
    # Check imports
    assert len(stats["imports"]) == 1
    assert stats["imports"][0]["module"] == "env"
    assert stats["imports"][0]["field"] == "log"
    assert stats["imports"][0]["kind"] == 0
    
    # Check exports
    assert len(stats["exports"]) == 1
    assert stats["exports"][0]["name"] == "main"
    assert stats["exports"][0]["kind"] == 0
    
    # Check custom sections
    assert "name" in stats["custom_sections"]

def test_invalid_wasm(fs):
    path = Path("/tmp/invalid.wasm")
    fs.create_file(path, contents=b'junk')
    
    stats = analyze_wasm(path)
    assert "error" in stats

def test_wrong_magic(fs):
    path = Path("/tmp/wrong.wasm")
    fs.create_file(path, contents=b'ABCD\x01\x00\x00\x00')
    
    stats = analyze_wasm(path)
    assert "error" in stats
    assert "magic" in stats["error"].lower()
