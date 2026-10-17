"""
Caddy Service modülü birim testleri.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.caddy_service import CaddyService
from utils import constants

import unittest


class TestCaddyService(unittest.TestCase):
    """CaddyService sınıfı testleri."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self._orig_caddyfile_path = constants.CADDYFILE_PATH
        self._orig_logs_dir = constants.LOGS_DIR
        constants.CADDYFILE_PATH = self.temp_dir / "config" / "Caddyfile"
        constants.LOGS_DIR = self.temp_dir / "logs"
        self.service = CaddyService()

    def tearDown(self):
        import shutil
        constants.CADDYFILE_PATH = self._orig_caddyfile_path
        constants.LOGS_DIR = self._orig_logs_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_caddyfile(self):
        """Caddyfile oluşturma testi."""
        site_root = str(self.temp_dir)
        caddyfile = self.service.generate_caddyfile(site_root, port=8080)

        self.assertTrue(caddyfile.exists())
        content = caddyfile.read_text(encoding="utf-8")
        self.assertIn(":8080", content)
        self.assertTrue(site_root in content or site_root.replace("\\", "/") in content)
        self.assertIn("file_server", content)
        self.assertIn("encode gzip", content)
        self.assertIn("/ahws-health", content)

    def test_generate_caddyfile_default_port(self):
        """Varsayılan port ile Caddyfile oluşturma testi."""
        site_root = str(self.temp_dir)
        caddyfile = self.service.generate_caddyfile(site_root)

        content = caddyfile.read_text(encoding="utf-8")
        self.assertIn(":80", content)

    def test_create_caddyfile_alias_both_arg_orders(self):
        """create_caddyfile hem (port, site_root) hem (site_root, port) desteklemeli."""
        site_root = str(self.temp_dir)
        cf1 = self.service.create_caddyfile(8081, site_root)
        self.assertIn(":8081", cf1.read_text(encoding="utf-8"))

        cf2 = self.service.create_caddyfile(site_root, 8082)
        self.assertIn(":8082", cf2.read_text(encoding="utf-8"))

    def test_get_status(self):
        """Servis durumu testi."""
        status = self.service.get_status()
        self.assertEqual(status["name"], "AHWS-Caddy")
        self.assertIn("is_installed", status)
        self.assertIn("is_running", status)

    # ─── HATA-08: Caddyfile sadece config dizinine yazılmalı ─────────
    def test_generate_caddyfile_writes_only_to_config_dir(self):
        """
        generate_caddyfile() Caddyfile'i SADECE constants.CADDYFILE_PATH'e yazmalı,
        site_root klasörüne YAZMAMALIdır.
        HATA-08 düzeltmesini doğrular.
        """
        site_root = str(self.temp_dir)
        caddyfile = self.service.generate_caddyfile(site_root, port=8080)

        # site_root'ta Caddyfile OLMAMALI
        site_caddyfile = self.temp_dir / "Caddyfile"
        self.assertFalse(site_caddyfile.exists(),
                         "Caddyfile site_root'ta olusturulmamali")

        # Config dizininde OLMALI
        self.assertTrue(caddyfile.exists(),
                        "Caddyfile config dizininde olusturulmali")


if __name__ == "__main__":
    unittest.main()