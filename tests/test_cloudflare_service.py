"""
Cloudflare Service modülü birim testleri.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.cloudflare_service import CloudflareService

import unittest


class TestCloudflareService(unittest.TestCase):
    """CloudflareService sınıfı testleri."""

    def setUp(self):
        self.service = CloudflareService()

    def test_validate_token_valid(self):
        """Geçerli token testi."""
        # JWT formatında geçerli bir token
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        self.assertTrue(self.service.validate_token(valid_token))

    def test_validate_token_invalid(self):
        """Geçersiz token testi."""
        self.assertFalse(self.service.validate_token(""))
        self.assertFalse(self.service.validate_token("invalid-token"))
        self.assertFalse(self.service.validate_token("abc.def"))

    def test_get_status(self):
        """Servis durumu testi."""
        status = self.service.get_status()
        self.assertEqual(status["name"], "Cloudflared")
        self.assertIn("is_installed", status)
        self.assertIn("is_running", status)


if __name__ == "__main__":
    unittest.main()