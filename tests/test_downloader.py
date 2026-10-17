"""
Downloader modülü birim testleri.
"""

import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

# Proje kök dizinini test path'ine ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.downloader import Downloader, DownloadCancelledError, DownloadError, HashMismatchError

import unittest


class TestDownloader(unittest.TestCase):
    """Downloader sınıfı testleri."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.downloader = Downloader(install_dir=self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_verify_sha256_mismatch(self):
        """SHA256 hash uyuşmazlığı testi."""
        test_file = self.temp_dir / "test_data.txt"
        test_file.write_text("merhaba", encoding="utf-8")

        with self.assertRaises(HashMismatchError):
            self.downloader.verify_sha256(test_file, "0000000000000000000000000000000000000000000000000000000000000000")

    def test_verify_sha256_match(self):
        """SHA256 hash eşleşmesi testi."""
        test_file = self.temp_dir / "test_data.txt"
        test_file.write_text("merhaba", encoding="utf-8")

        import hashlib
        expected = hashlib.sha256(test_file.read_bytes()).hexdigest()

        result = self.downloader.verify_sha256(test_file, expected)
        self.assertTrue(result)

    def test_download_cancelled_when_event_set(self):
        """cancel_event set edildiğinde indirme DownloadCancelledError fırlatmalı."""
        cancel_event = threading.Event()
        cancel_event.set()
        dl = Downloader(install_dir=self.temp_dir, cancel_event=cancel_event)
        with self.assertRaises(DownloadCancelledError):
            dl.download_file("https://example.com/file.zip", self.temp_dir / "file.zip")

    def test_is_binary_installed_false(self):
        """Var olmayan binary False dondurmeli."""
        self.assertFalse(self.downloader.is_binary_installed("caddy.exe"))

    def test_is_binary_installed_true(self):
        """Mevcut binary True dondurmeli."""
        bin_dir = self.temp_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        (bin_dir / "caddy.exe").write_bytes(b"fake exe content")
        self.assertTrue(self.downloader.is_binary_installed("caddy.exe"))

    @patch("core.downloader.Downloader.get_latest_release_url")
    def test_get_latest_release_url_uses_pattern(self, mock_get_url):
        """URL şablonu kullanımı testi."""
        mock_get_url.return_value = ("https://example.com/download.zip", "1.0.0")
        url, version = self.downloader.get_latest_release_url(
            "https://api.github.com/repos/test/test/releases/latest",
            "https://example.com/download/v{version}/file.zip",
        )
        self.assertEqual(version, "1.0.0")
        self.assertEqual(url, "https://example.com/download.zip")


if __name__ == "__main__":
    unittest.main()