from fetchext.packer import ExtensionPacker
from fetchext.crx import CrxDecoder

def test_pack_extension(tmp_path):
    # Create a dummy extension
    source_dir = tmp_path / "extension"
    source_dir.mkdir()
    (source_dir / "manifest.json").write_text('{"name": "Test", "version": "1.0"}')
    (source_dir / "script.js").write_text('console.log("Hello");')
    
    output_crx = tmp_path / "test.crx"
    
    packer = ExtensionPacker()
    packer.pack(source_dir, output_crx)
    
    assert output_crx.exists()
    assert output_crx.stat().st_size > 0
    
    # Verify key was generated
    key_path = tmp_path / "test.pem"
    assert key_path.exists()
    
    # Verify CRX structure
    offset = CrxDecoder.get_zip_offset(output_crx)
    assert offset > 0
    
    ext_id = CrxDecoder.get_id(output_crx)
    assert len(ext_id) == 32

def test_pack_with_existing_key(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()
    (source_dir / "manifest.json").write_text('{"name": "Test", "version": "1.0"}')
    
    output_crx = tmp_path / "test.crx"
    key_path = tmp_path / "mykey.pem"
    
    packer = ExtensionPacker()
    # Generate key first
    packer.generate_key(key_path)
    
    packer.pack(source_dir, output_crx, key_path=key_path)
    
    assert output_crx.exists()
    
    # Verify ID matches key
    ext_id = CrxDecoder.get_id(output_crx)
    assert len(ext_id) == 32
