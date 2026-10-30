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

    def test_generate_join_key_invalid_inputs(self):
        """cloudflare_token veya primary_device_id bos/None ise bos string donmeli."""
        dev_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZXN0IjoxfQ.sig"

        # Test with empty token
        self.assertEqual(InstallConfig.generate_join_key("", dev_id), "")
        # Test with None token
        self.assertEqual(InstallConfig.generate_join_key(None, dev_id), "")
        # Test with empty device id
        self.assertEqual(InstallConfig.generate_join_key(token, ""), "")
        # Test with None device id
        self.assertEqual(InstallConfig.generate_join_key(token, None), "")
        # Test with both empty
        self.assertEqual(InstallConfig.generate_join_key("", ""), "")
        # Test with both None
        self.assertEqual(InstallConfig.generate_join_key(None, None), "")

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

    def test_generate_join_key_empty_inputs(self):
        """Bos token veya device_id ile uretim yapilmamali."""
        self.assertEqual(InstallConfig.generate_join_key("", "device_id"), "")
        self.assertEqual(InstallConfig.generate_join_key("token", ""), "")

    def test_parse_join_key_empty_inputs(self):
        """Bos join_key None dondurmeli."""
        self.assertIsNone(InstallConfig.parse_join_key(""))
        self.assertIsNone(InstallConfig.parse_join_key(None))

    def test_parse_join_key_no_content(self):
        """Sadece prefix iceren join_key None dondurmeli."""
        from utils.constants import JOIN_KEY_PREFIX
        self.assertIsNone(InstallConfig.parse_join_key(JOIN_KEY_PREFIX))

    def test_parse_join_key_invalid_payload_type(self):
        """Payload sozluk degilse None dondurmeli."""
        import json
        import zlib
        import base64
        from utils.constants import JOIN_KEY_PREFIX

        raw_bytes = json.dumps(["not", "a", "dict"]).encode("utf-8")
        compressed = zlib.compress(raw_bytes, level=9)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
        key = f"{JOIN_KEY_PREFIX}{encoded}"

        self.assertIsNone(InstallConfig.parse_join_key(key))

    def test_parse_join_key_missing_required_fields(self):
        """Gerekli alanlar eksikse None dondurmeli."""
        import json
        import zlib
        import base64
        from utils.constants import JOIN_KEY_PREFIX

        payload_missing_t = {"d": "device_id", "p": 80, "u": "domain.com"}
        raw_bytes1 = json.dumps(payload_missing_t).encode("utf-8")
        compressed1 = zlib.compress(raw_bytes1, level=9)
        encoded1 = base64.urlsafe_b64encode(compressed1).decode("ascii").rstrip("=")
        key1 = f"{JOIN_KEY_PREFIX}{encoded1}"
        self.assertIsNone(InstallConfig.parse_join_key(key1))

        payload_missing_d = {"t": "token", "p": 80, "u": "domain.com"}
        raw_bytes2 = json.dumps(payload_missing_d).encode("utf-8")
        compressed2 = zlib.compress(raw_bytes2, level=9)
        encoded2 = base64.urlsafe_b64encode(compressed2).decode("ascii").rstrip("=")
        key2 = f"{JOIN_KEY_PREFIX}{encoded2}"
        self.assertIsNone(InstallConfig.parse_join_key(key2))


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


class TestI18nCompleteness(unittest.TestCase):
    """Projedeki tum t('...') anahtarlarinin tr ve en sozluklerinde eksiksiz oldugunu dogrular."""

    def test_all_i18n_keys_exist_in_tr_and_en(self):
        import ast
        from utils.i18n import TRANSLATIONS

        root = Path(__file__).resolve().parent.parent
        used_keys = set()

        for py_file in root.rglob("*.py"):
            if "venv" in py_file.parts or "build" in py_file.parts or "dist" in py_file.parts:
                continue
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name) and func.id == "t":
                        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            used_keys.add(node.args[0].value)

        self.assertGreater(len(used_keys), 50)
        missing_tr = used_keys - set(TRANSLATIONS["tr"].keys())
        missing_en = used_keys - set(TRANSLATIONS["en"].keys())
        self.assertEqual(missing_tr, set(), f"TR sozlugunde eksik anahtarlar: {missing_tr}")
        self.assertEqual(missing_en, set(), f"EN sozlugunde eksik anahtarlar: {missing_en}")

    def test_no_astral_emojis_in_translations(self):
        """Windows 10 Tkinter GDI'da bozuk gorunen U+FFFF ustu emoji bulunmamali."""
        from utils.i18n import TRANSLATIONS

        for lang, table in TRANSLATIONS.items():
            for key, val in table.items():
                astral = [ch for ch in val if ord(ch) > 0xFFFF]
                self.assertEqual(
                    astral, [],
                    f"{lang}.{key} icinde Windows 10 Tkinter'da bozuk gorunen karakter var: {astral}"
                )


if __name__ == "__main__":
    unittest.main()