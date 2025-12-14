import pytest
from unittest.mock import patch, MagicMock
from fetchext.commands.query import handle_query


@pytest.fixture
def mock_history():
    with patch("fetchext.commands.query.HistoryManager") as mock:
        yield mock.return_value


def test_query_json(mock_history, capsys):
    args = MagicMock()
    args.sql = "SELECT * FROM history"
    args.json = True
    args.csv = False

    mock_history.execute_query.return_value = [{"id": 1, "action": "download"}]

    handle_query(args)

    captured = capsys.readouterr()
    assert '"id": 1' in captured.out
    assert '"action": "download"' in captured.out


def test_query_csv(mock_history, capsys):
    args = MagicMock()
    args.sql = "SELECT * FROM history"
    args.json = False
    args.csv = True

    mock_history.execute_query.return_value = [{"id": 1, "action": "download"}]

    handle_query(args)

    captured = capsys.readouterr()
    assert "id,action" in captured.out
    assert "1,download" in captured.out


def test_query_table(mock_history, capsys):
    args = MagicMock()
    args.sql = "SELECT * FROM history"
    args.json = False
    args.csv = False

    mock_history.execute_query.return_value = [{"id": 1, "action": "download"}]

    handle_query(args)

    captured = capsys.readouterr()
    # Rich table output is hard to assert exactly, but we can check for content
    assert "id" in captured.out
    assert "action" in captured.out
    assert "download" in captured.out
    assert "1 rows returned" in captured.out


def test_query_error(mock_history, capsys):
    args = MagicMock()
    args.sql = "SELECT * FROM invalid"

    mock_history.execute_query.side_effect = Exception("Table not found")

    with pytest.raises(SystemExit):
        handle_query(args)

    captured = capsys.readouterr()
    assert "Query failed" in captured.out
