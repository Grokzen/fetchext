import pytest
from fetchext.hooks import HookManager, HookContext

@pytest.fixture
def mock_hooks_dir(tmp_path):
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    return hooks_dir

def test_hook_context_initialization():
    ctx = HookContext(
        extension_id="test_id",
        browser="chrome",
        config={"key": "value"},
        args={"arg": 1}
    )
    assert ctx.extension_id == "test_id"
    assert ctx.browser == "chrome"
    assert ctx.config == {"key": "value"}
    assert ctx.args == {"arg": 1}
    assert ctx.cancel is False
    assert ctx.result is None

def test_hook_cancellation(mock_hooks_dir):
    # Create a hook that cancels the operation
    hook_code = """
def pre_download(context):
    context.cancel = True
"""
    (mock_hooks_dir / "cancel_hook.py").write_text(hook_code)
    
    manager = HookManager(mock_hooks_dir)
    ctx = HookContext(extension_id="test", browser="chrome")
    
    manager.run_hook("pre_download", ctx)
    
    assert ctx.cancel is True

def test_hook_result_modification(mock_hooks_dir):
    # Create a hook that modifies the result
    hook_code = """
def post_analysis(context):
    if context.result:
        context.result['modified'] = True
"""
    (mock_hooks_dir / "modify_hook.py").write_text(hook_code)
    
    manager = HookManager(mock_hooks_dir)
    ctx = HookContext(extension_id="test", browser="chrome")
    ctx.result = {"original": True}
    
    manager.run_hook("post_analysis", ctx)
    
    assert ctx.result["modified"] is True
    assert ctx.result["original"] is True

def test_hook_context_access(mock_hooks_dir):
    # Create a hook that checks config
    hook_code = """
def pre_download(context):
    if context.config.get('stop_me'):
        context.cancel = True
"""
    (mock_hooks_dir / "config_hook.py").write_text(hook_code)
    
    manager = HookManager(mock_hooks_dir)
    
    # Case 1: Config says stop
    ctx1 = HookContext(extension_id="test", browser="chrome", config={"stop_me": True})
    manager.run_hook("pre_download", ctx1)
    assert ctx1.cancel is True
    
    # Case 2: Config says go
    ctx2 = HookContext(extension_id="test", browser="chrome", config={"stop_me": False})
    manager.run_hook("pre_download", ctx2)
    assert ctx2.cancel is False
