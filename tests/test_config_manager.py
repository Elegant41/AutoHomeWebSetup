"""
ConfigManager modülü birim testleri.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config_manager import ConfigManager

import unittest


class TestConfigManager(unittest.TestCase):
    """ConfigManager sınıfı testleri."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "install_config.json"
        self.manager = ConfigManager(self.config_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """Kaydetme ve yükleme testi."""
        data = {"test_key": "test_value", "number": 42}
        self.manager.save(data)

        loaded = self.manager.load()
        self.assertEqual(loaded["test_key"], "test_value")
        self.assertEqual(loaded["number"], 42)
        self.assertIn("install_date", loaded)

    def test_load_empty(self):
        """Boş dosya yükleme testi."""
        data = self.manager.load()
        self.assertEqual(data, {})

    def test_exists(self):
        """Dosya varlık kontrolü testi."""
        self.assertFalse(self.manager.exists())
        self.manager.save({"test": "data"})
        self.assertTrue(self.manager.exists())

    def test_delete(self):
        """Dosya silme testi."""
        self.manager.save({"test": "data"})
        self.assertTrue(self.manager.exists())
        self.manager.delete()
        self.assertFalse(self.manager.exists())

    def test_installed_services(self):
        """Kurulu servis testi."""
        services = ["service1", "service2"]
        self.manager.update_installed_services(services)
        self.assertEqual(self.manager.get_installed_services(), services)

    def test_created_directories(self):
        """Oluşturulan dizinler testi."""
        dirs = ["C:/dir1", "C:/dir2"]
        self.manager.update_created_directories(dirs)
        self.assertEqual(self.manager.get_created_directories(), dirs)


if __name__ == "__main__":
    unittest.main()