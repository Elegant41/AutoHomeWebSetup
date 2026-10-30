import pytest
import zlib
import base64
import json
from core.models import InstallConfig
from utils import constants

class TestInstallConfig:
    def test_parse_join_key_invalid_json(self):
        """Test parse_join_key with a malformed JSON payload."""
        malformed_payload = b"{invalid_json:"
        compressed = zlib.compress(malformed_payload, level=9)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
        join_key = f"{constants.JOIN_KEY_PREFIX}{encoded}"

        result = InstallConfig.parse_join_key(join_key)
        assert result is None

    def test_parse_join_key_valid(self):
        """Test parse_join_key with a valid join key."""
        join_key = InstallConfig.generate_join_key(
            cloudflare_token="test_token",
            primary_device_id="test_device_id",
            caddy_port=8080,
            public_domain="test.domain.com"
        )

        result = InstallConfig.parse_join_key(join_key)
        assert result is not None
        assert result["cloudflare_token"] == "test_token"
        assert result["primary_device_id"] == "test_device_id"
        assert result["caddy_port"] == 8080
        assert result["public_domain"] == "test.domain.com"
