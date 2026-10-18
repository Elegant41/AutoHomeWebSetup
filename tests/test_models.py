import base64
import json
import zlib
import pytest
from core.models import InstallConfig
from utils.constants import JOIN_KEY_PREFIX

def test_parse_join_key_none():
    assert InstallConfig.parse_join_key(None) is None
    assert InstallConfig.parse_join_key("") is None
    assert InstallConfig.parse_join_key("   ") is None

def test_parse_join_key_invalid_prefix():
    assert InstallConfig.parse_join_key("INVALID-PREFIX") is None
    assert InstallConfig.parse_join_key("AHWS2-somebase64") is None

def test_parse_join_key_empty_b64():
    assert InstallConfig.parse_join_key(JOIN_KEY_PREFIX) is None
    assert InstallConfig.parse_join_key(f"{JOIN_KEY_PREFIX}   ") is None

def test_parse_join_key_invalid_b64():
    assert InstallConfig.parse_join_key(f"{JOIN_KEY_PREFIX}invalid_b64!@#") is None

def _create_compressed_payload(payload):
    raw_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw_bytes, level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"{JOIN_KEY_PREFIX}{encoded}"

def test_parse_join_key_invalid_json():
    # Provide valid base64 but decompressing yields non-JSON or non-dict
    # Non-JSON string
    raw_bytes = b"not a json string"
    compressed = zlib.compress(raw_bytes, level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    assert InstallConfig.parse_join_key(f"{JOIN_KEY_PREFIX}{encoded}") is None

    # JSON but not dict
    raw_bytes = json.dumps(["list", "instead", "of", "dict"]).encode("utf-8")
    compressed = zlib.compress(raw_bytes, level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    assert InstallConfig.parse_join_key(f"{JOIN_KEY_PREFIX}{encoded}") is None

def test_parse_join_key_missing_fields():
    # Missing 't'
    payload_no_t = {"d": "device_id_123", "p": 8080, "u": "example.com"}
    join_key_no_t = _create_compressed_payload(payload_no_t)
    assert InstallConfig.parse_join_key(join_key_no_t) is None

    # Missing 'd'
    payload_no_d = {"t": "token_123", "p": 8080, "u": "example.com"}
    join_key_no_d = _create_compressed_payload(payload_no_d)
    assert InstallConfig.parse_join_key(join_key_no_d) is None

    # Empty 't'
    payload_empty_t = {"t": "", "d": "device_id_123"}
    join_key_empty_t = _create_compressed_payload(payload_empty_t)
    assert InstallConfig.parse_join_key(join_key_empty_t) is None

    # Empty 'd'
    payload_empty_d = {"t": "token_123", "d": ""}
    join_key_empty_d = _create_compressed_payload(payload_empty_d)
    assert InstallConfig.parse_join_key(join_key_empty_d) is None

def test_parse_join_key_success():
    join_key = InstallConfig.generate_join_key(
        cloudflare_token="cf_token_123",
        primary_device_id="device_id_456",
        caddy_port=9090,
        public_domain="test.domain.com"
    )

    parsed = InstallConfig.parse_join_key(join_key)

    assert parsed is not None
    assert parsed["cloudflare_token"] == "cf_token_123"
    assert parsed["primary_device_id"] == "device_id_456"
    assert parsed["caddy_port"] == 9090
    assert parsed["public_domain"] == "test.domain.com"

def test_generate_join_key_empty_fields():
    # Generate should return empty string if required fields are missing
    assert InstallConfig.generate_join_key("", "device_id_456") == ""
    assert InstallConfig.generate_join_key("cf_token_123", "") == ""
    assert InstallConfig.generate_join_key("", "") == ""
