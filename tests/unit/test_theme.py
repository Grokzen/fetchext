from fetchext.theme import Theme

def test_theme_constants():
    assert Theme.ICON_SUCCESS == "✅"
    assert Theme.COLOR_SUCCESS == "green"

def test_theme_formatting():
    msg = Theme.format_success("Done")
    assert "✅ Done" in msg
    assert "[green]" in msg

    msg = Theme.format_error("Fail")
    assert "❌ Fail" in msg
    assert "[red]" in msg
