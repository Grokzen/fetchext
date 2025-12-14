import pytest
from fetchext.plugins.hooks import HookManager, HookContext


@pytest.fixture
def hooks_dir(tmp_path):
    d = tmp_path / "hooks"
    d.mkdir()
    return d


def test_load_hooks(hooks_dir):
    # Create a dummy hook file
    hook_file = hooks_dir / "my_hook.py"
    hook_file.write_text("""
def pre_download(ctx):
    ctx.metadata = {"test": "pre"}

def post_download(ctx):
    ctx.metadata["test"] = "post"
""")

    manager = HookManager(hooks_dir)
    assert len(manager.hooks["pre_download"]) == 1
    assert len(manager.hooks["post_download"]) == 1


def test_run_hooks(hooks_dir):
    hook_file = hooks_dir / "test_hook.py"
    hook_file.write_text("""
def pre_download(ctx):
    ctx.version = "1.0.0"
""")

    manager = HookManager(hooks_dir)
    ctx = HookContext(extension_id="abc", browser="chrome")

    manager.run_hook("pre_download", ctx)
    assert ctx.version == "1.0.0"


def test_hook_exception_handling(hooks_dir, caplog):
    hook_file = hooks_dir / "bad_hook.py"
    hook_file.write_text("""
def pre_download(ctx):
    raise ValueError("Boom")
""")

    manager = HookManager(hooks_dir)
    ctx = HookContext(extension_id="abc", browser="chrome")

    # Should not raise exception
    manager.run_hook("pre_download", ctx)

    assert "Error in hook pre_download: Boom" in caplog.text


def test_ignore_underscore_files(hooks_dir):
    hook_file = hooks_dir / "_hidden.py"
    hook_file.write_text("""
def pre_download(ctx):
    pass
""")
    manager = HookManager(hooks_dir)
    assert len(manager.hooks["pre_download"]) == 0
