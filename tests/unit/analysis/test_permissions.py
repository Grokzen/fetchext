from unittest.mock import patch
from fetchext.analysis.permissions import PermissionMatrixGenerator

def test_generate_permission_matrix(tmp_path):
    # Create dummy extension files
    (tmp_path / "ext1.crx").touch()
    (tmp_path / "ext2.zip").touch()
    
    generator = PermissionMatrixGenerator()
    
    with patch("fetchext.analysis.permissions.ExtensionInspector") as MockInspector:
        inspector = MockInspector.return_value
        
        def get_manifest_side_effect(path):
            if "ext1.crx" in str(path):
                return {"permissions": ["tabs", "storage"]}
            if "ext2.zip" in str(path):
                return {"permissions": ["storage", "cookies"], "host_permissions": ["<all_urls>"]}
            return {}
            
        inspector.get_manifest.side_effect = get_manifest_side_effect
        
        results = generator.generate(tmp_path)
        
        assert "permissions" in results
        assert "extensions" in results
        assert "matrix" in results
        
        perms = results["permissions"]
        assert "tabs" in perms
        assert "storage" in perms
        assert "cookies" in perms
        assert "<all_urls>" in perms
        
        matrix = results["matrix"]
        assert matrix["ext1.crx"]["tabs"] is True
        assert matrix["ext1.crx"]["cookies"] is False
        assert matrix["ext2.zip"]["cookies"] is True
        assert matrix["ext2.zip"]["<all_urls>"] is True

def test_generate_permission_matrix_empty(tmp_path):
    generator = PermissionMatrixGenerator()
    results = generator.generate(tmp_path)
    assert results["permissions"] == []
    assert results["extensions"] == []
    assert results["matrix"] == {}
