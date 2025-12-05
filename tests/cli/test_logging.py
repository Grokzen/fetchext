import logging
from fetchext.cli import main

def test_verbose_flag(mocker):
    mocker.patch("sys.argv", ["fext", "-v", "download", "chrome", "https://example.com/id"])
    
    # Mock core.download_extension to avoid actual work
    mocker.patch("fetchext.core.download_extension")
    
    # Mock logger
    mock_logger = mocker.patch("fetchext.cli.logger")
    
    main()
    
    # Verify setLevel was called with DEBUG
    mock_logger.setLevel.assert_called_with(logging.DEBUG)

def test_quiet_flag(mocker):
    mocker.patch("sys.argv", ["fext", "-q", "download", "chrome", "https://example.com/id"])
    
    mock_download = mocker.patch("fetchext.core.download_extension")
    
    mock_logger = mocker.patch("fetchext.cli.logger")
    
    main()
    
    # Verify setLevel was called with ERROR
    mock_logger.setLevel.assert_called_with(logging.ERROR)
    
    # Verify download called with show_progress=False
    mock_download.assert_called_with(
        "chrome", 
        "https://example.com/id", 
        mocker.ANY, 
        save_metadata=False, 
        extract=False, 
        show_progress=False
    )
    
    # Verify info logs were NOT called
    mock_logger.info.assert_not_called()

def test_default_logging(mocker):
    mocker.patch("sys.argv", ["fext", "download", "chrome", "https://example.com/id"])
    
    mock_download = mocker.patch("fetchext.core.download_extension")
    
    mock_logger = mocker.patch("fetchext.cli.logger")
    
    main()
    
    # Verify setLevel was NOT called (uses default INFO)
    mock_logger.setLevel.assert_not_called()
    
    # Verify download called with show_progress=True
    mock_download.assert_called_with(
        "chrome", 
        "https://example.com/id", 
        mocker.ANY, 
        save_metadata=False, 
        extract=False, 
        show_progress=True
    )
    
    # Verify info logs WERE called
    assert mock_logger.info.called
