from unittest.mock import MagicMock, patch
from pathlib import Path
from fetchext.batch import BatchProcessor

class TestBatchProcessor:
    def test_process_calls_executor(self, fs):
        # Create a dummy batch file
        tmp_path = Path("/tmp/test_batch")
        fs.create_dir(tmp_path)
        batch_file = tmp_path / "batch.txt"
        fs.create_file(batch_file, contents="chrome abc\nedge def")
        
        processor = BatchProcessor()
        
        # Mock ThreadPoolExecutor AND as_completed
        with patch("concurrent.futures.ThreadPoolExecutor") as MockExecutor, \
             patch("concurrent.futures.as_completed") as mock_as_completed:
            
            mock_executor_instance = MockExecutor.return_value
            mock_executor_instance.__enter__.return_value = mock_executor_instance
            
            # Make submit return a mock future
            mock_future = MagicMock()
            mock_executor_instance.submit.return_value = mock_future
            
            # Make as_completed yield the mock futures immediately
            mock_as_completed.return_value = [mock_future, mock_future]
            
            processor.process(batch_file, tmp_path, max_workers=2)
            
            # Verify executor was initialized with correct workers
            MockExecutor.assert_called_with(max_workers=2)
            
            # Verify submit was called twice
            assert mock_executor_instance.submit.call_count == 2

    def test_process_line_chrome(self, fs):
        tmp_path = Path("/tmp/test_batch")
        fs.create_dir(tmp_path)
        processor = BatchProcessor()
        
        with patch("fetchext.batch.ChromeDownloader") as MockDownloader:
            mock_instance = MockDownloader.return_value
            mock_instance.extract_id.return_value = "abc"
            
            processor._process_line("chrome abc", tmp_path)
            
            mock_instance.extract_id.assert_called_with("abc")
            # Verify show_progress=False is passed
            mock_instance.download.assert_called_with("abc", tmp_path, show_progress=False)

    def test_process_line_invalid_format(self, fs, caplog):
        import logging
        caplog.set_level(logging.WARNING)
        tmp_path = Path("/tmp/test_batch")
        fs.create_dir(tmp_path)
        processor = BatchProcessor()
        processor._process_line("invalid_line", tmp_path)
        assert "Invalid line format" in caplog.text

    def test_process_line_unsupported_browser(self, fs, caplog):
        import logging
        caplog.set_level(logging.WARNING)
        tmp_path = Path("/tmp/test_batch")
        fs.create_dir(tmp_path)
        processor = BatchProcessor()
        processor._process_line("safari abc", tmp_path)
        assert "Unsupported browser" in caplog.text
