import json
import zipfile
from pathlib import Path
from fetchext.stats import RepoAnalyzer

def create_dummy_extension(fs, path, manifest):
    """Helper to create a dummy extension file."""
    # Create a real zip file in memory
    from io import BytesIO
    buf = BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr('manifest.json', json.dumps(manifest))
    
    # Write to fake fs
    fs.create_file(path, contents=buf.getvalue())

def test_empty_repo(fs):
    fs.create_dir("/repo")
    analyzer = RepoAnalyzer()
    stats = analyzer.scan(Path("/repo"))
    
    assert stats.total_files == 0
    assert stats.mv2_count == 0
    assert stats.mv3_count == 0

def test_scan_repo(fs):
    fs.create_dir("/repo")
    
    # MV2 Extension
    create_dummy_extension(fs, "/repo/ext1.zip", {
        "manifest_version": 2,
        "name": "Ext 1",
        "permissions": ["tabs", "http://*/*"]
    })
    
    # MV3 Extension
    create_dummy_extension(fs, "/repo/ext2.crx", {
        "manifest_version": 3,
        "name": "Ext 2",
        "permissions": ["storage"],
        "host_permissions": ["https://google.com/*"]
    })
    
    # Invalid Extension
    fs.create_file("/repo/broken.zip", contents=b"not a zip")
    
    analyzer = RepoAnalyzer()
    stats = analyzer.scan(Path("/repo"))
    
    assert stats.total_files == 3
    assert stats.mv2_count == 1
    assert stats.mv3_count == 1
    assert len(stats.errors) == 1
    
    assert stats.permissions["tabs"] == 1
    assert stats.permissions["storage"] == 1
    assert stats.host_permissions["http://*/*"] == 1
    assert stats.host_permissions["https://google.com/*"] == 1

def test_permission_heuristics(fs):
    fs.create_dir("/repo")
    create_dummy_extension(fs, "/repo/ext.zip", {
        "manifest_version": 2,
        "permissions": ["<all_urls>", "tabs", "https://example.com/"]
    })
    
    analyzer = RepoAnalyzer()
    stats = analyzer.scan(Path("/repo"))
    
    assert stats.host_permissions["<all_urls>"] == 1
    assert stats.host_permissions["https://example.com/"] == 1
    assert stats.permissions["tabs"] == 1
