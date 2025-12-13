from unittest.mock import MagicMock, patch
from pathlib import Path
from fetchext.analysis.yara import YaraScanner
from fetchext.secrets import SecretScanner

class TestMemoryOptimization:
    
    @patch("fetchext.analysis.yara.CrxDecoder")
    @patch("fetchext.analysis.yara.ZipFile")
    @patch("fetchext.analysis.yara.tempfile.NamedTemporaryFile")
    @patch("fetchext.analysis.yara.os.unlink")
    def test_yara_large_file_handling(self, mock_unlink, mock_temp, mock_zip, mock_crx, fs):
        fs.create_file("rules.yar")
        fs.create_file("test.crx")
        
        mock_crx.get_zip_offset.return_value = 0
        
        # Setup mocks
        mock_zf_instance = mock_zip.return_value
        
        # Mock a large file info
        mock_info = MagicMock()
        mock_info.filename = "large_file.bin"
        mock_info.file_size = 15 * 1024 * 1024 # 15MB
        mock_info.is_dir.return_value = False
        mock_zf_instance.infolist.return_value = [mock_info]
        
        # Mock file opening and reading
        mock_source = MagicMock()
        mock_source.read.side_effect = [b"chunk1", b"chunk2", b""] # Stream chunks
        mock_zf_instance.open.return_value.__enter__.return_value = mock_source
        
        # Mock temp file
        mock_tmp = MagicMock()
        mock_tmp.name = "/tmp/tempfile"
        mock_temp.return_value.__enter__.return_value = mock_tmp
        
        # Mock yara module
        mock_yara = MagicMock()
        with patch.dict("sys.modules", {"yara": mock_yara}):
            scanner = YaraScanner(Path("rules.yar"))
            # Mock scan_file to avoid real yara matching
            scanner.scan_file = MagicMock(return_value=[])
            
            scanner.scan_archive(Path("test.crx"))
            
            # Verify temp file usage
            mock_temp.assert_called()
            mock_tmp.write.assert_called()
            scanner.scan_file.assert_called_with(Path("/tmp/tempfile"))
            mock_unlink.assert_called_with("/tmp/tempfile")
            
            # Verify streaming read
            assert mock_source.read.call_count == 3

    @patch("fetchext.secrets.open_extension_archive")
    def test_secrets_streaming(self, mock_open_archive):
        mock_zf = MagicMock()
        mock_open_archive.return_value.__enter__.return_value = mock_zf
        
        mock_zf.namelist.return_value = ["test.js"]
        
        # Mock streaming file object
        mock_file = MagicMock()
        # iter returns lines
        mock_file.__iter__.return_value = [b"var api_key = '12345';\n", b"var x = 1;\n"]
        mock_zf.open.return_value.__enter__.return_value = mock_file
        
        scanner = SecretScanner()
        # Mock _scan_line to verify it's called
        scanner._scan_line = MagicMock(return_value=[])
        
        scanner.scan_extension(Path("test.crx"))
        
        # Verify zf.open was used instead of zf.read
        mock_zf.open.assert_called_with("test.js")
        mock_zf.read.assert_not_called()
        
        # Verify _scan_line called for each line
        assert scanner._scan_line.call_count == 2
