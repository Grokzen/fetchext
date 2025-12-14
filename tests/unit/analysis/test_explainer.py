from fetchext.analysis.explainer import explain_permission, get_all_permissions


def test_explain_known_permission():
    result = explain_permission("tabs")
    assert result is not None
    assert "description" in result
    assert "risk" in result
    assert result["risk"] == "High"


def test_explain_unknown_permission():
    result = explain_permission("nonexistent_permission")
    assert result is None


def test_explain_host_permission():
    result = explain_permission("https://google.com/*")
    assert result is not None
    assert result["risk"] == "Medium"
    assert "google.com" in result["description"]


def test_explain_all_urls():
    result = explain_permission("<all_urls>")
    assert result is not None
    assert result["risk"] == "Critical"


def test_get_all_permissions():
    db = get_all_permissions()
    assert isinstance(db, dict)
    assert "tabs" in db
    assert "storage" in db
