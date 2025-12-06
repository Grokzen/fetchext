import pytest
import json
from fetchext.server import generate_update_manifest

@pytest.fixture
def mock_inspector(mocker):
    return mocker.patch("fetchext.server.ExtensionInspector")

@pytest.fixture
def mock_crx_decoder(mocker):
    return mocker.patch("fetchext.server.CrxDecoder")

def test_generate_update_manifest_chrome(tmp_path, mock_inspector, mock_crx_decoder):
    # Setup
    d = tmp_path / "extensions"
    d.mkdir()
    (d / "ext1.crx").touch()
    
    # Mock Inspector
    inspector_instance = mock_inspector.return_value
    inspector_instance.get_manifest.return_value = {"version": "1.0", "name": "Test Ext"}
    
    # Mock CrxDecoder
    mock_crx_decoder.get_id.return_value = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    
    # Run
    generate_update_manifest(d, "http://example.com")
    
    # Verify
    xml_file = d / "update.xml"
    assert xml_file.exists()
    content = xml_file.read_text()
    assert 'appid="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"' in content
    assert 'codebase="http://example.com/ext1.crx"' in content
    assert 'version="1.0"' in content

def test_generate_update_manifest_firefox(tmp_path, mock_inspector):
    # Setup
    d = tmp_path / "extensions"
    d.mkdir()
    (d / "ext1.xpi").touch()
    
    # Mock Inspector
    inspector_instance = mock_inspector.return_value
    inspector_instance.get_manifest.return_value = {
        "version": "2.0", 
        "browser_specific_settings": {"gecko": {"id": "test@example.com"}}
    }
    
    # Run
    generate_update_manifest(d, "http://example.com")
    
    # Verify
    json_file = d / "updates.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert "test@example.com" in data["addons"]
    assert data["addons"]["test@example.com"]["updates"][0]["version"] == "2.0"
    assert data["addons"]["test@example.com"]["updates"][0]["update_link"] == "http://example.com/ext1.xpi"

def test_generate_update_manifest_mixed(tmp_path, mock_inspector, mock_crx_decoder):
    # Setup
    d = tmp_path / "extensions"
    d.mkdir()
    (d / "ext1.crx").touch()
    (d / "ext2.xpi").touch()
    
    # Mock Inspector
    inspector_instance = mock_inspector.return_value
    def side_effect(path):
        if path.suffix == ".crx":
            return {"version": "1.0"}
        else:
            return {"version": "2.0", "browser_specific_settings": {"gecko": {"id": "test@example.com"}}}
    inspector_instance.get_manifest.side_effect = side_effect
    
    # Mock CrxDecoder
    mock_crx_decoder.get_id.return_value = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    
    # Run
    generate_update_manifest(d, "http://example.com")
    
    # Verify both exist
    assert (d / "update.xml").exists()
    assert (d / "updates.json").exists()

def test_run_server(tmp_path, mocker):
    # Mock socketserver.TCPServer
    mock_server = mocker.patch("fetchext.server.socketserver.TCPServer")
    mock_server_instance = mock_server.return_value
    mock_server_instance.__enter__.return_value = mock_server_instance
    
    # Mock os.chdir
    mock_chdir = mocker.patch("fetchext.server.os.chdir")
    
    from fetchext.server import run_server
    
    # Create a dummy directory
    d = tmp_path / "serve_dir"
    d.mkdir()
    
    # Run server (it should call serve_forever)
    run_server(d, port=9000)
    
    # Verify
    mock_chdir.assert_called_with(d.resolve())
    mock_server.assert_called_once()
    mock_server_instance.serve_forever.assert_called_once()
