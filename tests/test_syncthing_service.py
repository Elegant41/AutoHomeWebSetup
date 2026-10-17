"""
Syncthing Service modülü birim testleri.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.syncthing_service import SyncthingService
from utils import constants

import unittest


class TestSyncthingService(unittest.TestCase):
    """SyncthingService sınıfı testleri."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.orig_home = constants.SYNCTHING_HOME_DIR
        constants.SYNCTHING_HOME_DIR = self.temp_dir / "syncthing_home"
        self.service = SyncthingService()

    def tearDown(self):
        constants.SYNCTHING_HOME_DIR = self.orig_home
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_initial_config(self):
        """İlk yapılandırma oluşturma testi."""
        config_path = self.service.generate_initial_config(
            home_dir=self.temp_dir / "syncthing_home",
            gui_port=8385,
            api_key="test-api-key-1234567890abcdef",
        )

        self.assertTrue(config_path.exists())
        content = config_path.read_text(encoding="utf-8")
        self.assertIn("test-api-key-1234567890abcdef", content)
        self.assertIn("8385", content)

    def test_generate_api_key(self):
        """API anahtarı üretme testi."""
        api_key = self.service._generate_api_key(32)
        self.assertEqual(len(api_key), 32)
        self.assertTrue(api_key.isalnum())

        # Farklı çağrılar farklı anahtarlar üretmeli
        api_key2 = self.service._generate_api_key(32)
        self.assertNotEqual(api_key, api_key2)

    def test_get_status(self):
        """Servis durumu testi."""
        status = self.service.get_status()
        self.assertEqual(status["name"], "AHWS-Syncthing")
        self.assertIn("is_installed", status)
        self.assertIn("is_running", status)

    # ─── HATA-01: get_devices() API list response ────────────────────
    @patch("services.syncthing_service.requests.get")
    def test_get_devices_returns_list_directly(self, mock_get):
        """
        Syncthing API /rest/config/devices doğrudan liste döndürür.
        Eski .get('devices', []) yerine direkt response.json() kullanılmalı.
        HATA-01 düzeltmesini doğrular.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"deviceID": "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH", "name": "Test"},
        ]
        mock_get.return_value = mock_response

        devices = self.service.get_devices()
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["deviceID"], "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH")

    # ─── HATA-02: get_folders() API list response ────────────────────
    @patch("services.syncthing_service.requests.get")
    def test_get_folders_returns_list_directly(self, mock_get):
        """
        Syncthing API /rest/config/folders doğrudan liste döndürür.
        HATA-02 düzeltmesini doğrular.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "auto-home-web", "path": "C:/site"},
        ]
        mock_get.return_value = mock_response

        folders = self.service.get_folders()
        self.assertIsInstance(folders, list)
        self.assertEqual(len(folders), 1)
        self.assertEqual(folders[0]["id"], "auto-home-web")

    # ─── HATA-03: add_device() PUT payload doğru format ──────────────
    @patch("services.syncthing_service.requests.put")
    @patch("services.syncthing_service.requests.get")
    def test_add_device_puts_list_payload(self, mock_get, mock_put):
        """
        add_device() PUT çağrısında JSON payload direkt liste olmalı,
        {"devices": [...]} dict olmamalı.
        HATA-03 düzeltmesini doğrular.
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []  # Boş cihaz listesi
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        test_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        self.service.add_device(test_device_id, "Test Cihaz")

        mock_put.assert_called_once()
        call_kwargs = mock_put.call_args[1]  # keyword args
        payload = call_kwargs.get("json")

        # Payload liste olmalı, dict olmamalı
        self.assertIsInstance(payload, list, "PUT payload direkt liste olmalı, dict degil")
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["deviceID"], test_device_id)

    # ─── HATA-05: share_folder() cihaz formatı doğru ─────────────────
    @patch("services.syncthing_service.requests.put")
    @patch("services.syncthing_service.requests.get")
    def test_share_folder_device_format(self, mock_get, mock_put):
        """
        share_folder() içindeki klasör 'devices' alanı
        [{"deviceID": "...", "encryptionPassword": ""}] formatında olmalı,
        string listesi ["deviceID"] olmamalı.
        HATA-05 düzeltmesini doğrular.
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []  # Klasör yok
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        test_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        self.service.share_folder("auto-home-web", "C:/site", [test_device_id])

        mock_put.assert_called_once()
        call_kwargs = mock_put.call_args[1]
        payload = call_kwargs.get("json")

        # Payload liste olmalı
        self.assertIsInstance(payload, list, "PUT payload direkt liste olmali")
        self.assertEqual(len(payload), 1)
        folder = payload[0]
        # Klasör devices alanı dict listesi olmalı
        self.assertIsInstance(folder["devices"], list)
        if folder["devices"]:
            self.assertIsInstance(folder["devices"][0], dict, "devices icinde dict olmali")
            self.assertIn("deviceID", folder["devices"][0])

    # ─── HATA-04: share_folder() PUT payload liste formatı ───────────
    @patch("services.syncthing_service.requests.put")
    @patch("services.syncthing_service.requests.get")
    def test_share_folder_puts_list_payload(self, mock_get, mock_put):
        """
        share_folder() PUT çağrısında JSON payload direkt liste olmalı.
        HATA-04 düzeltmesini doğrular.
        """
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = []
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        self.service.share_folder("test-folder", "C:/test", [])

        mock_put.assert_called_once()
        payload = mock_put.call_args[1].get("json")
        self.assertIsInstance(payload, list, "PUT payload list olmali, dict degil")

    def test_generate_initial_config_preserves_existing_devices(self):
        """Mevcut config.xml güncellenirken eşleşmiş cihazlar ve klasörler korunmalı."""
        home_dir = self.temp_dir / "syncthing_home"
        home_dir.mkdir(parents=True, exist_ok=True)
        config_path = home_dir / "config.xml"
        config_path.write_text(
            """<?xml version="1.0" encoding="utf-8"?>
<configuration version="52">
    <folder id="auto-home-web" label="AHWS Web Site" path="C:/old_site" type="sendreceive">
        <device id="AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"></device>
    </folder>
    <device id="AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH" name="Yedek"></device>
    <gui enabled="true" tls="false">
        <address>127.0.0.1:8384</address>
        <apikey>old-key</apikey>
    </gui>
</configuration>""",
            encoding="utf-8",
        )

        self.service.generate_initial_config(
            home_dir=home_dir,
            gui_port=8385,
            api_key="new-api-key-999",
            default_folder_path="C:/new_site",
        )

        updated_xml = config_path.read_text(encoding="utf-8")
        self.assertIn("new-api-key-999", updated_xml)
        self.assertIn("127.0.0.1:8385", updated_xml)
        self.assertIn("AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH", updated_xml)
        self.assertIn("auto-home-web", updated_xml)

    @patch("services.syncthing_service.requests.put")
    @patch("services.syncthing_service.requests.get")
    def test_remove_device_cleans_devices_and_folders(self, mock_get, mock_put):
        """remove_device() cihazı hem devices hem folders listesinden kaldırmalı."""
        target_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        local_id = "1111111-2222222-3333333-4444444-5555555-6666666-7777777-8888888"

        resp_devices = MagicMock(status_code=200)
        resp_devices.json.return_value = [
            {"deviceID": local_id, "name": "Local"},
            {"deviceID": target_id, "name": "Remote"},
        ]
        resp_folders = MagicMock(status_code=200)
        resp_folders.json.return_value = [
            {
                "id": "auto-home-web",
                "path": "C:/site",
                "devices": [{"deviceID": local_id}, {"deviceID": target_id}],
            }
        ]
        mock_get.side_effect = [resp_devices, resp_folders]
        mock_put.return_value = MagicMock(status_code=200)

        self.service.remove_device(target_id)
        self.assertEqual(mock_put.call_count, 2)


if __name__ == "__main__":
    unittest.main()