"""
Tests for data models in core.models.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import InstallConfig, NodeRole, ProgressEvent, ServiceStatus, InstallResult
from utils import constants

class TestInstallConfig(unittest.TestCase):
    """InstallConfig serialization, instantiation, and join key tests."""

    def test_build_install_config_defaults(self):
        """InstallConfig varsayilan degerleri dogru olmali."""
        config = InstallConfig()
        self.assertEqual(config.caddy_port, constants.CADDY_DEFAULT_PORT)
        self.assertEqual(config.node_role, NodeRole.PRIMARY)
        self.assertEqual(config.site_root_path, "")
        self.assertEqual(config.cloudflare_token, "")
        self.assertEqual(config.syncthing_gui_port, constants.SYNCTHING_GUI_PORT)
        self.assertEqual(config.install_dir, str(constants.INSTALL_DIR))

    def test_install_config_to_dict(self):
        """InstallConfig.to_dict() dogru sozluk uretmeli."""
        config = InstallConfig()
        config.site_root_path = "C:/site"
        config.cloudflare_token = "eyJtest.test.test"
        config.node_role = NodeRole.SECONDARY
        config.prevent_sleep = False
        config.public_domain = "example.com"
        config.primary_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD"
        config.syncthing_api_key = "secret"
        config.local_device_id = "LOCAL-DEVICE"

        d = config.to_dict()
        self.assertEqual(d["site_root_path"], "C:/site")
        self.assertEqual(d["node_role"], "secondary")
        self.assertEqual(d["cloudflare_token"], "eyJtest.test.test")
        self.assertEqual(d["prevent_sleep"], False)
        self.assertEqual(d["public_domain"], "example.com")
        self.assertEqual(d["primary_device_id"], "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD")
        self.assertEqual(d["syncthing_api_key"], "secret")
        self.assertEqual(d["local_device_id"], "LOCAL-DEVICE")
        self.assertIn("caddy_port", d)
        self.assertIn("install_dir", d)

    def test_install_config_from_dict_roundtrip(self):
        """to_dict() ve from_dict() roundtrip tutarli olmali."""
        original = InstallConfig()
        original.site_root_path = "C:/mysite"
        original.caddy_port = 8080
        original.node_role = NodeRole.SECONDARY
        original.primary_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        original.cloudflare_token = "token123"
        original.public_domain = "test.com"
        original.prevent_sleep = False
        original.syncthing_gui_port = 9090
        original.syncthing_api_key = "apikey123"
        original.local_device_id = "LOCAL-123"

        restored = InstallConfig.from_dict(original.to_dict())
        self.assertEqual(restored.site_root_path, original.site_root_path)
        self.assertEqual(restored.caddy_port, original.caddy_port)
        self.assertEqual(restored.node_role, original.node_role)
        self.assertEqual(restored.primary_device_id, original.primary_device_id)
        self.assertEqual(restored.cloudflare_token, original.cloudflare_token)
        self.assertEqual(restored.public_domain, original.public_domain)
        self.assertEqual(restored.prevent_sleep, original.prevent_sleep)
        self.assertEqual(restored.syncthing_gui_port, original.syncthing_gui_port)
        self.assertEqual(restored.syncthing_api_key, original.syncthing_api_key)
        self.assertEqual(restored.local_device_id, original.local_device_id)
        self.assertEqual(restored.install_dir, original.install_dir)

    def test_from_dict_invalid_role(self):
        """from_dict invalid role gelirse PRIMARY yapmali."""
        data = {"node_role": "invalid_role"}
        restored = InstallConfig.from_dict(data)
        self.assertEqual(restored.node_role, NodeRole.PRIMARY)

    def test_join_key_roundtrip(self):
        """generate_join_key ve parse_join_key tam uyumlu olmali."""
        dev_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZXN0IjoxfQ.sig"
        key = InstallConfig.generate_join_key(
            primary_device_id=dev_id,
            cloudflare_token=token,
            caddy_port=8080,
            public_domain="example.com",
        )
        self.assertTrue(key.startswith("AHWS1-"))
        parsed = InstallConfig.parse_join_key(key)
        self.assertEqual(parsed["primary_device_id"], dev_id)
        self.assertEqual(parsed["cloudflare_token"], token)
        self.assertEqual(parsed["caddy_port"], 8080)
        self.assertEqual(parsed["public_domain"], "example.com")

    def test_generate_join_key_empty(self):
        """Bos token veya device_id ile uretim bos donmeli."""
        self.assertEqual(InstallConfig.generate_join_key("", "device_id"), "")
        self.assertEqual(InstallConfig.generate_join_key("token", ""), "")

    def test_parse_invalid_join_key_returns_none(self):
        """Gecersiz Join Key None dondurmeli."""
        self.assertIsNone(InstallConfig.parse_join_key(""))
        self.assertIsNone(InstallConfig.parse_join_key("INVALID-KEY"))
        self.assertIsNone(InstallConfig.parse_join_key("AHWS1-invalid_base64"))

    def test_parse_join_key_invalid_json(self):
        """Gecerli base64/zlib ama gecersiz JSON veya dict degilse None donmeli."""
        import base64
        import zlib

        # Array instead of dict
        compressed = zlib.compress(b'["not", "a", "dict"]')
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
        key = f"AHWS1-{encoded}"
        self.assertIsNone(InstallConfig.parse_join_key(key))

        # Missing required fields in dict
        compressed2 = zlib.compress(b'{"wrong": "field"}')
        encoded2 = base64.urlsafe_b64encode(compressed2).decode("ascii").rstrip("=")
        key2 = f"AHWS1-{encoded2}"
        self.assertIsNone(InstallConfig.parse_join_key(key2))


class TestOtherDataclasses(unittest.TestCase):
    """ProgressEvent, ServiceStatus ve InstallResult dataclass instantiation tests."""

    def test_progress_event_instantiation(self):
        """ProgressEvent basariyla olusturulabilmeli."""
        event = ProgressEvent(message="Test message", percentage=50)
        self.assertEqual(event.message, "Test message")
        self.assertEqual(event.percentage, 50)
        self.assertFalse(event.is_error)
        self.assertFalse(event.is_complete)
        self.assertFalse(event.is_cancelled)

    def test_service_status_instantiation(self):
        """ServiceStatus basariyla olusturulabilmeli."""
        status = ServiceStatus(name="TestService", is_installed=True)
        self.assertEqual(status.name, "TestService")
        self.assertTrue(status.is_installed)
        self.assertFalse(status.is_running)
        self.assertIsNone(status.error)

    def test_install_result_instantiation(self):
        """InstallResult basariyla olusturulabilmeli."""
        result = InstallResult(success=True, message="Success")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Success")
        self.assertEqual(result.device_id, "")
        self.assertFalse(result.rollback_performed)
        self.assertEqual(result.completed_steps, [])

        # Check defaults for list factory
        result.completed_steps.append("step1")
        result2 = InstallResult(success=False, message="Fail")
        self.assertEqual(result2.completed_steps, [])

if __name__ == "__main__":
    unittest.main()
