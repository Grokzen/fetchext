import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from fetchext.optimizer import optimize_image, optimize_extension

class TestOptimizer(unittest.TestCase):

    @patch("fetchext.optimizer.Image.open")
    @patch("pathlib.Path.stat")
    def test_optimize_image_success(self, mock_stat, mock_open):
        # Setup
        mock_path = MagicMock(spec=Path)
        mock_path.suffix = ".png"
        mock_path.name = "test.png"
        mock_path.with_suffix.return_value = MagicMock()
        
        # Mock original size
        mock_stat.return_value.st_size = 1000
        
        # Mock image context manager
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        mock_img.format = "PNG"
        
        # Mock save behavior - we need to simulate the temp file being smaller
        # The optimize_image function calls stat() on the temp path to check size
        # So we need to handle the stat call for the temp path
        
        # We need to distinguish between calls to stat() on original path and temp path
        # But since we are mocking Path.stat globally, it's tricky.
        # Let's mock the path object's stat method instead if possible, but optimize_image calls path.stat()
        
        # Let's use side_effect for stat
        def stat_side_effect():
            m = MagicMock()
            # If it's the temp path (which we can't easily identify by instance identity in this setup)
            # Let's assume the second call is for the temp path
            return m
            
        # Actually, let's just mock the path instances passed to the function
        # The function receives 'path'.
        
        path_mock = MagicMock(spec=Path)
        path_mock.suffix = ".png"
        path_mock.name = "test.png"
        path_mock.stat.return_value.st_size = 1000
        
        temp_mock = MagicMock(spec=Path)
        temp_mock.stat.return_value.st_size = 500 # Smaller size
        
        path_mock.with_suffix.return_value = temp_mock
        
        # Run
        success, orig, new = optimize_image(path_mock)
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(orig, 1000)
        self.assertEqual(new, 500)
        temp_mock.replace.assert_called_with(path_mock)
        mock_img.save.assert_called()

    @patch("fetchext.optimizer.Image.open")
    def test_optimize_image_no_reduction(self, mock_open):
        # Setup
        path_mock = MagicMock(spec=Path)
        path_mock.suffix = ".jpg"
        path_mock.name = "test.jpg"
        path_mock.stat.return_value.st_size = 1000
        
        temp_mock = MagicMock(spec=Path)
        temp_mock.stat.return_value.st_size = 1200 # Larger size
        
        path_mock.with_suffix.return_value = temp_mock
        
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        mock_img.format = "JPEG"
        
        # Run
        success, orig, new = optimize_image(path_mock)
        
        # Verify
        self.assertFalse(success)
        self.assertEqual(orig, 1000)
        self.assertEqual(new, 1000)
        temp_mock.replace.assert_not_called()
        temp_mock.unlink.assert_called()

    @patch("fetchext.optimizer.optimize_image")
    def test_optimize_extension(self, mock_optimize):
        # Setup
        mock_dir = MagicMock(spec=Path)
        mock_dir.exists.return_value = True
        mock_dir.is_dir.return_value = True
        
        file1 = MagicMock(spec=Path)
        file1.is_file.return_value = True
        file1.suffix = ".png"
        
        file2 = MagicMock(spec=Path)
        file2.is_file.return_value = True
        file2.suffix = ".txt" # Should be ignored
        
        file3 = MagicMock(spec=Path)
        file3.is_file.return_value = True
        file3.suffix = ".jpg"
        
        mock_dir.rglob.return_value = [file1, file2, file3]
        
        # Mock optimize results
        # file1: success
        # file3: fail
        mock_optimize.side_effect = [
            (True, 1000, 500),
            (False, 800, 800)
        ]
        
        # Run
        stats = optimize_extension(mock_dir)
        
        # Verify
        self.assertEqual(stats["total_files"], 2)
        self.assertEqual(stats["optimized_files"], 1)
        self.assertEqual(stats["original_size"], 1800)
        self.assertEqual(stats["new_size"], 1300)
        self.assertEqual(stats["saved_bytes"], 500)

