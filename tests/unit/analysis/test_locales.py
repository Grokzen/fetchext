import zipfile
import json
from pathlib import Path
from fetchext.analysis.locales import inspect_locales

def test_inspect_locales(fs):
    zip_path = Path("/test.zip")
    manifest = {"default_locale": "en"}
    messages_en = {"hello": {"message": "Hello"}}
    messages_fr = {"hello": {"message": "Bonjour"}}
    
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("_locales/en/messages.json", json.dumps(messages_en))
        zf.writestr("_locales/fr/messages.json", json.dumps(messages_fr))
        
    results = inspect_locales(zip_path)
    
    assert results["default_locale"] == "en"
    assert "en" in results["supported_locales"]
    assert "fr" in results["supported_locales"]
    assert results["details"]["en"]["message_count"] == 1
    assert results["details"]["fr"]["message_count"] == 1

def test_inspect_locales_no_locales(fs):
    zip_path = Path("/empty.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", "{}")
        
    results = inspect_locales(zip_path)
    assert results["default_locale"] is None
    assert len(results["supported_locales"]) == 0

def test_inspect_locales_broken_json(fs):
    zip_path = Path("/broken.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", "{}")
        zf.writestr("_locales/es/messages.json", "{broken")
        
    results = inspect_locales(zip_path)
    assert "es" in results["supported_locales"]
    assert "error" in results["details"]["es"]
