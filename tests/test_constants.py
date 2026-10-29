import pytest
from utils.constants import clean_cloudflare_token

def test_clean_cloudflare_token_empty():
    assert clean_cloudflare_token("") == ""
    assert clean_cloudflare_token(None) == ""

def test_clean_cloudflare_token_pure():
    token = "eyJhIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJ0IjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJzIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYifQ=="
    assert clean_cloudflare_token(token) == token

def test_clean_cloudflare_token_with_spaces():
    token = "eyJhIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJ0IjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJzIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYifQ=="
    assert clean_cloudflare_token(f"  {token}  ") == token

def test_clean_cloudflare_token_with_quotes():
    token = "eyJhIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJ0IjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJzIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYifQ=="
    assert clean_cloudflare_token(f'"{token}"') == token
    assert clean_cloudflare_token(f"'{token}'") == token

def test_clean_cloudflare_token_in_command_string():
    token = "eyJhIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJ0IjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYiLCJzIjoiY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjYifQ=="
    cmd = f"cloudflared.exe service install {token}"
    assert clean_cloudflare_token(cmd) == token

def test_clean_cloudflare_token_no_match():
    assert clean_cloudflare_token("invalid_token") == "invalid_token"
    assert clean_cloudflare_token("this is not a token") == "this is not a token"
