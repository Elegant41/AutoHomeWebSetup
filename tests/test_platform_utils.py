import tempfile
import os
from pathlib import Path

from utils.platform_utils import is_valid_binary

def test_is_valid_binary_with_valid_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"fake binary content")
        temp_path = temp_file.name

    try:
        assert is_valid_binary(temp_path) is True
    finally:
        os.remove(temp_path)

def test_is_valid_binary_with_empty_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Default min_size=1, should be False
        assert is_valid_binary(temp_path) is False
        # If min_size=0, should be True
        assert is_valid_binary(temp_path, min_size=0) is True
    finally:
        os.remove(temp_path)

def test_is_valid_binary_with_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        assert is_valid_binary(temp_dir) is False

def test_is_valid_binary_with_non_existent_path():
    non_existent = Path(tempfile.gettempdir()) / "this_file_does_not_exist_12345.exe"
    assert is_valid_binary(non_existent) is False

def test_is_valid_binary_with_invalid_type():
    assert is_valid_binary(None) is False
