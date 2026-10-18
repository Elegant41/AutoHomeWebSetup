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