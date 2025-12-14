import json
import pytest
from fetchext.cli import main


def test_search_json_output(mocker, capsys):
    mocker.patch("sys.argv", ["fext", "search", "firefox", "query", "--json"])

    mock_results = [
        {"name": "Test", "slug": "test", "guid": "123", "url": "http://test"}
    ]

    mock_downloader = mocker.Mock()
    mock_downloader.search.return_value = mock_results
    mocker.patch("fetchext.core.FirefoxDownloader", return_value=mock_downloader)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output == mock_results


def test_inspect_json_output(mocker, capsys):
    mocker.patch("sys.argv", ["fext", "inspect", "test.crx", "--json"])

    mock_manifest = {"name": "Test Extension", "version": "1.0"}

    mock_inspector = mocker.Mock()
    mock_inspector.get_manifest.return_value = mock_manifest
    mocker.patch("fetchext.core.ExtensionInspector", return_value=mock_inspector)

    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output == mock_manifest
