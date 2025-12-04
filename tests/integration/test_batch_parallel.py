import time
from unittest.mock import patch
from fetchext.batch import BatchProcessor

class TestBatchParallelism:
    def test_parallel_execution_speed(self, tmp_path):
        """
        Verify that 4 tasks taking 1 second each finish in ~1 second with 4 workers,
        proving they ran in parallel.
        """
        batch_file = tmp_path / "parallel_test.txt"
        # Create 4 lines
        batch_file.write_text("\n".join([f"chrome id_{i}" for i in range(4)]))
        
        processor = BatchProcessor()
        
        # Mock ChromeDownloader to sleep for 1 second instead of downloading
        with patch("fetchext.batch.ChromeDownloader") as MockDownloader:
            mock_instance = MockDownloader.return_value
            mock_instance.extract_id.side_effect = lambda x: x # Return ID as is
            
            def slow_download(id, output_dir):
                time.sleep(1.0)
                
            mock_instance.download.side_effect = slow_download
            
            start_time = time.time()
            # Run with 4 workers
            processor.process(batch_file, tmp_path, max_workers=4)
            end_time = time.time()
            
            duration = end_time - start_time
            
            # It should take slightly more than 1 second, but definitely less than 2
            # (Sequential would take 4+ seconds)
            assert duration < 2.0
            assert duration >= 1.0
