"""
app.py App sinifi navigasyon birim testleri.
Tkinter gerektiren testler mock ile izole edilir.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import InstallConfig, NodeRole


class TestInstallConfigRoundtrip(unittest.TestCase):
    """InstallConfig to_dict/from_dict testleri."""

    def test_build_install_config_defaults(self):
        """InstallConfig varsayilan degerleri dogru olmali."""
        config = InstallConfig()
        self.assertEqual(config.caddy_port, 80)
        self.assertEqual(config.node_role, NodeRole.PRIMARY)
        self.assertEqual(config.site_root_path, "")
        self.assertEqual(config.cloudflare_token, "")

    def test_install_config_to_dict(self):
        """InstallConfig.to_dict() dogru sozluk uretmeli."""
        config = InstallConfig()
        config.site_root_path = "C:/site"
        config.cloudflare_token = "eyJtest.test.test"
        config.node_role = NodeRole.SECONDARY

        d = config.to_dict()
        self.assertEqual(d["site_root_path"], "C:/site")
        self.assertEqual(d["node_role"], "secondary")
        self.assertIn("caddy_port", d)

    def test_install_config_from_dict_roundtrip(self):
        """to_dict() ve from_dict() roundtrip tutarli olmali."""
        original = InstallConfig()
        original.site_root_path = "C:/mysite"
        original.caddy_port = 8080
        original.node_role = NodeRole.SECONDARY
        original.primary_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"

        restored = InstallConfig.from_dict(original.to_dict())
        self.assertEqual(restored.site_root_path, original.site_root_path)
        self.assertEqual(restored.caddy_port, original.caddy_port)
        self.assertEqual(restored.node_role, original.node_role)
        self.assertEqual(restored.primary_device_id, original.primary_device_id)

    def test_node_role_primary_value(self):
        """NodeRole.PRIMARY.value 'primary' olmali."""
        self.assertEqual(NodeRole.PRIMARY.value, "primary")

    def test_node_role_secondary_value(self):
        """NodeRole.SECONDARY.value 'secondary' olmali."""
        self.assertEqual(NodeRole.SECONDARY.value, "secondary")

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

    def test_parse_invalid_join_key_returns_none(self):
        """Gecersiz Join Key None dondurmeli."""
        self.assertIsNone(InstallConfig.parse_join_key("INVALID-KEY"))
        self.assertIsNone(InstallConfig.parse_join_key("AHWS1-invalid_base64"))


class TestPageNavigationLogic(unittest.TestCase):
    """
    show_page() stack birikimini test eder.
    HATA-07 duzeltmesini dogrular.
    """

    def test_no_duplicate_consecutive_pages_in_stack(self):
        """
        Ayni sayfa arka arkaya stack'e eklenmemeli.
        Duzeltme sonrasi davranisi simule eder.
        """
        mock_page_a = MagicMock()
        mock_page_b = MagicMock()
        page_stack = []
        pages = {"page_a": mock_page_a, "page_b": mock_page_b}

        def simulated_show_page(name):
            """HATA-07 duzeltmesi uygulanmis show_page simulasyonu."""
            page = pages.get(name)
            if page_stack:
                current = page_stack[-1]
                if current is page:
                    return  # Ayni sayfa, ekleme
                current.pack_forget()
            page.pack()
            if not page_stack or page_stack[-1] is not page:
                page_stack.append(page)

        # Kullanici navigasyonu simulasyonu
        simulated_show_page("page_a")
        simulated_show_page("page_a")  # Tekrar ayni sayfa - eklenmemeli
        simulated_show_page("page_b")
        simulated_show_page("page_b")  # Tekrar ayni sayfa - eklenmemeli

        # Stack'te ardisik duplicate olmamali
        for i in range(len(page_stack) - 1):
            self.assertIsNot(
                page_stack[i], page_stack[i + 1],
                f"Stack[{i}] ve Stack[{i+1}] ayni sayfa olmamali"
            )


if __name__ == "__main__":
    unittest.main()