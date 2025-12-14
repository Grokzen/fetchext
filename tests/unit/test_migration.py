import json
from fetchext.migration import MV3Migrator


def test_migrate_mv2_to_mv3(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()

    manifest = {
        "manifest_version": 2,
        "name": "Test",
        "version": "1.0",
        "permissions": ["tabs", "http://*/*", "<all_urls>"],
        "browser_action": {"default_popup": "popup.html"},
        "background": {"scripts": ["bg.js"], "persistent": False},
        "content_security_policy": "script-src 'self'; object-src 'self'",
        "web_accessible_resources": ["image.png"],
    }

    (source_dir / "manifest.json").write_text(json.dumps(manifest))
    (source_dir / "bg.js").write_text("console.log('bg');")

    migrator = MV3Migrator(source_dir)
    migrator.migrate()

    # Verify manifest changes
    new_manifest = json.loads((source_dir / "manifest.json").read_text())

    assert new_manifest["manifest_version"] == 3
    assert "host_permissions" in new_manifest
    assert "http://*/*" in new_manifest["host_permissions"]
    assert "tabs" in new_manifest["permissions"]
    assert "http://*/*" not in new_manifest["permissions"]

    assert "action" in new_manifest
    assert "browser_action" not in new_manifest

    assert "service_worker" in new_manifest["background"]
    assert new_manifest["background"]["service_worker"] == "bg.js"
    assert "scripts" not in new_manifest["background"]
    assert "persistent" not in new_manifest["background"]

    assert isinstance(new_manifest["content_security_policy"], dict)
    assert "extension_pages" in new_manifest["content_security_policy"]

    assert isinstance(new_manifest["web_accessible_resources"][0], dict)
    assert "image.png" in new_manifest["web_accessible_resources"][0]["resources"]


def test_migrate_multiple_bg_scripts(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()

    manifest = {
        "manifest_version": 2,
        "name": "Test",
        "version": "1.0",
        "background": {"scripts": ["bg1.js", "bg2.js"]},
    }

    (source_dir / "manifest.json").write_text(json.dumps(manifest))

    migrator = MV3Migrator(source_dir)
    migrator.migrate()

    new_manifest = json.loads((source_dir / "manifest.json").read_text())
    assert new_manifest["background"]["service_worker"] == "background_wrapper.js"

    wrapper = source_dir / "background_wrapper.js"
    assert wrapper.exists()
    content = wrapper.read_text()
    assert "importScripts('bg1.js');" in content
    assert "importScripts('bg2.js');" in content


def test_migrate_war_smart_matches(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()

    manifest = {
        "manifest_version": 2,
        "name": "Test",
        "version": "1.0",
        "content_scripts": [
            {"matches": ["*://*.example.com/*"], "js": ["content.js"]},
            {"matches": ["https://google.com/*"], "css": ["style.css"]},
        ],
        "web_accessible_resources": ["images/icon.png"],
    }

    (source_dir / "manifest.json").write_text(json.dumps(manifest))

    migrator = MV3Migrator(source_dir)
    migrator.migrate()

    new_manifest = json.loads((source_dir / "manifest.json").read_text())

    war = new_manifest["web_accessible_resources"]
    assert len(war) == 1
    # Should contain matches from content scripts
    assert set(war[0]["matches"]) == {"*://*.example.com/*", "https://google.com/*"}


def test_migrate_war_fallback(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()

    manifest = {
        "manifest_version": 2,
        "name": "Test",
        "version": "1.0",
        "web_accessible_resources": ["foo.png"],
    }

    (source_dir / "manifest.json").write_text(json.dumps(manifest))

    migrator = MV3Migrator(source_dir)
    migrator.migrate()

    new_manifest = json.loads((source_dir / "manifest.json").read_text())

    war = new_manifest["web_accessible_resources"]
    assert war[0]["matches"] == ["<all_urls>"]


def test_migrate_merge_actions(tmp_path):
    source_dir = tmp_path / "extension"
    source_dir.mkdir()

    manifest = {
        "manifest_version": 2,
        "name": "Test",
        "version": "1.0",
        "browser_action": {
            "default_popup": "popup.html",
            "default_title": "Browser Action",
        },
        "page_action": {
            "default_icon": "icon.png",
            "default_title": "Page Action",  # Should be overwritten or preserved?
        },
    }

    (source_dir / "manifest.json").write_text(json.dumps(manifest))

    migrator = MV3Migrator(source_dir)
    migrator.migrate()

    new_manifest = json.loads((source_dir / "manifest.json").read_text())

    assert "action" in new_manifest
    action = new_manifest["action"]
    assert action["default_popup"] == "popup.html"
    assert action["default_icon"] == "icon.png"
    # If conflict, what happens? Currently last one wins.
    # Let's assert that we at least have properties from both.
