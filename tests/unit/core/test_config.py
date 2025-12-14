from pathlib import Path
from fetchext.config import load_config, get_config_path


def test_get_config_path_xdg(mocker):
    mocker.patch.dict("os.environ", {"XDG_CONFIG_HOME": "/tmp/config"})
    assert get_config_path() == Path("/tmp/config/fext/config.toml")


def test_get_config_path_default(mocker):
    mocker.patch.dict("os.environ", {}, clear=True)
    mocker.patch("pathlib.Path.home", return_value=Path("/home/user"))
    assert get_config_path() == Path("/home/user/.config/fext/config.toml")


def test_load_config_no_file(mocker):
    mocker.patch("pathlib.Path.exists", return_value=False)
    assert load_config() == {}


def test_load_config_valid(fs):
    config_content = """
    [general]
    download_dir = "/tmp/downloads"
    save_metadata = true
    
    [batch]
    workers = 8
    """

    config_path = Path.home() / ".config" / "fext" / "config.toml"
    fs.create_file(config_path, contents=config_content)

    # Mock get_config_path to return this path
    # Since we are using pyfakefs, Path.home() works if we create the dir?
    # Actually pyfakefs mocks os.path and pathlib.Path.
    # But get_config_path uses Path.home().
    # Let's just mock get_config_path to be safe/explicit.

    # Wait, if we use fs, we don't need to mock get_config_path if we put the file in the right place.
    # But Path.home() might be system dependent.
    # Let's mock get_config_path in fetchext.config

    # Actually, let's just use the mocked fs and rely on get_config_path logic if we can control env.
    pass


def test_load_config_integration(fs, mocker):
    # Setup fake filesystem
    config_content = b"""
    [general]
    download_dir = "/tmp/downloads"
    save_metadata = true
    
    [batch]
    workers = 8
    """

    # Mock XDG_CONFIG_HOME to a known path in fake fs
    mocker.patch.dict("os.environ", {"XDG_CONFIG_HOME": "/config"})
    fs.create_file("/config/fext/config.toml", contents=config_content)

    config = load_config()

    assert config["general"]["download_dir"] == "/tmp/downloads"
    assert config["general"]["save_metadata"] is True
    assert config["batch"]["workers"] == 8


def test_load_config_invalid_toml(fs, mocker):
    from fetchext.exceptions import ConfigError
    import pytest

    mocker.patch.dict("os.environ", {"XDG_CONFIG_HOME": "/config"})
    fs.create_file("/config/fext/config.toml", contents="invalid toml [")

    # Should raise ConfigError on error
    with pytest.raises(ConfigError):
        load_config()


def test_load_config_invalid_type(fs, mocker):
    from fetchext.exceptions import ConfigError
    import pytest

    config_content = """
    [general]
    save_metadata = "not a boolean"
    """

    mocker.patch.dict("os.environ", {"XDG_CONFIG_HOME": "/config"})
    fs.create_file("/config/fext/config.toml", contents=config_content)

    with pytest.raises(ConfigError, match="must be of type bool"):
        load_config()


def test_load_config_invalid_section(fs, mocker):
    from fetchext.exceptions import ConfigError
    import pytest

    # This is tricky because TOML parsers usually enforce structure.
    # But if we had something like:
    # general = "not a dict"
    # TOML parser might handle it, but our schema expects a dict.

    config_content = """
    general = "not a dict"
    """

    mocker.patch.dict("os.environ", {"XDG_CONFIG_HOME": "/config"})
    fs.create_file("/config/fext/config.toml", contents=config_content)

    with pytest.raises(ConfigError, match="Section 'general' must be a dictionary"):
        load_config()
