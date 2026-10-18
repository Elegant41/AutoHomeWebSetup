import pytest
from unittest.mock import patch
from pathlib import Path

from utils import resource_path

def test_resource_path_frozen():
    with patch("utils.resource_path._MEIPASS", "/tmp/meipass"):
        assert resource_path.resource_path("test/file.txt") == Path("/tmp/meipass/test/file.txt")

def test_resource_path_not_frozen():
    with patch("utils.resource_path._MEIPASS", None):
        expected = Path(resource_path.__file__).resolve().parent.parent / "test/file.txt"
        assert resource_path.resource_path("test/file.txt") == expected

def test_is_frozen_true():
    with patch("utils.resource_path._MEIPASS", "/tmp/meipass"):
        assert resource_path.is_frozen() is True

def test_is_frozen_false():
    with patch("utils.resource_path._MEIPASS", None):
        assert resource_path.is_frozen() is False
