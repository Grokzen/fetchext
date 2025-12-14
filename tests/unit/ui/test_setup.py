import pytest
from unittest.mock import patch
from fetchext.setup import run_setup


@pytest.fixture
def mock_config_path(tmp_path):
    config_file = tmp_path / "config.toml"
    with patch("fetchext.setup.get_config_path", return_value=config_file):
        yield config_file


@pytest.fixture
def mock_prompts():
    with (
        patch("fetchext.setup.Prompt.ask") as mock_prompt,
        patch("fetchext.setup.Confirm.ask") as mock_confirm,
        patch("fetchext.setup.IntPrompt.ask") as mock_int,
        patch("fetchext.setup.FloatPrompt.ask") as mock_float,
    ):
        yield mock_prompt, mock_confirm, mock_int, mock_float


def test_run_setup_new_file(mock_config_path, mock_prompts):
    mock_prompt, mock_confirm, mock_int, mock_float = mock_prompts

    # Setup inputs
    mock_prompt.return_value = "downloads"
    mock_confirm.side_effect = [True, False]  # save_metadata=True, extract=False
    mock_int.return_value = 8
    mock_float.return_value = 1.5

    run_setup()

    assert mock_config_path.exists()
    content = mock_config_path.read_text()

    assert 'download_dir = "downloads"' in content
    assert "save_metadata = true" in content
    assert "extract = false" in content
    assert "workers = 8" in content
    assert "rate_limit_delay = 1.5" in content


def test_run_setup_overwrite_cancel(mock_config_path, mock_prompts):
    mock_prompt, mock_confirm, mock_int, mock_float = mock_prompts

    # Create existing file
    mock_config_path.parent.mkdir(parents=True, exist_ok=True)
    mock_config_path.write_text("existing")

    # User says No to overwrite
    mock_confirm.return_value = False

    run_setup()

    # Content should be unchanged
    assert mock_config_path.read_text() == "existing"


def test_run_setup_overwrite_confirm(mock_config_path, mock_prompts):
    mock_prompt, mock_confirm, mock_int, mock_float = mock_prompts

    # Create existing file
    mock_config_path.parent.mkdir(parents=True, exist_ok=True)
    mock_config_path.write_text("existing")

    # User says Yes to overwrite
    # Then inputs for settings
    mock_confirm.side_effect = [
        True,
        False,
        True,
    ]  # Overwrite=True, Metadata=False, Extract=True
    mock_prompt.return_value = "."
    mock_int.return_value = 2
    mock_float.return_value = 0.5

    run_setup()

    content = mock_config_path.read_text()
    assert 'download_dir = "."' in content
    assert "extract = true" in content
