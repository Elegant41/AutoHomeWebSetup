import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import i18n

class TestI18n(unittest.TestCase):
    def setUp(self):
        # Store original language to restore after tests
        self.original_lang = i18n.get_language()

        # We also want to ensure a known clean state
        # Let's add a fake language and translation for testing to avoid
        # depending on actual translation keys which might change.
        self.original_translations = i18n._TRANSLATIONS

        i18n._TRANSLATIONS = {
            "tr": {
                "test_key": "Test çevirisi",
                "test_format": "Test {value}",
                "test_format_multi": "{name} - {age}"
            },
            "en": {
                "test_key": "Test translation",
                "test_format": "Test {value}",
                "test_format_multi": "{name} - {age}"
            }
        }
        i18n.set_language("tr")

    def tearDown(self):
        # Restore original state
        i18n._TRANSLATIONS = self.original_translations
        i18n.set_language(self.original_lang)

    def test_get_language(self):
        self.assertEqual(i18n.get_language(), "tr")

    def test_set_language_valid(self):
        i18n.set_language("en")
        self.assertEqual(i18n.get_language(), "en")

    def test_set_language_invalid(self):
        # Should not change language if lang_code is not in _TRANSLATIONS
        i18n.set_language("fr")
        self.assertEqual(i18n.get_language(), "tr")

    def test_t_existing_key(self):
        self.assertEqual(i18n.t("test_key"), "Test çevirisi")

        i18n.set_language("en")
        self.assertEqual(i18n.t("test_key"), "Test translation")

    def test_t_missing_key(self):
        self.assertEqual(i18n.t("missing_key"), "[missing_key]")

    def test_t_with_kwargs(self):
        self.assertEqual(i18n.t("test_format", value="123"), "Test 123")
        self.assertEqual(i18n.t("test_format_multi", name="Jules", age="30"), "Jules - 30")

    def test_t_with_invalid_kwargs(self):
        # Should return the original string if kwargs don't match the format string
        self.assertEqual(i18n.t("test_format", wrong_kwarg="123"), "Test {value}")

if __name__ == "__main__":
    unittest.main()
