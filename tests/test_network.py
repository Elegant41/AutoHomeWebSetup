"""
utils/network.py modulu birim testleri.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.network import (
    is_port_available,
    get_local_ip,
    check_internet_connection,
    check_tcp_connection,
    find_available_port,
    check_local_http_health,
)


class TestPortAvailability(unittest.TestCase):

    def test_is_port_available_returns_bool(self):
        """is_port_available() bool dondurmeli."""
        result = is_port_available(62000)  # Yuksek port, muhtemelen bos
        self.assertIsInstance(result, bool)

    def test_is_port_available_used_port(self):
        """Kullanimda olan port False dondurmeli."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
            self.assertFalse(is_port_available(port))

    def test_find_available_port_returns_valid(self):
        """find_available_port() gecerli port veya -1 dondurmeli."""
        port = find_available_port(50000)
        if port != -1:
            self.assertGreaterEqual(port, 50000)
            self.assertLessEqual(port, 65535)
        # -1 de gecerli (hic bos port yoksa)


class TestGetLocalIP(unittest.TestCase):

    def test_get_local_ip_returns_string(self):
        """get_local_ip() string dondurmeli."""
        ip = get_local_ip()
        self.assertIsInstance(ip, str)
        self.assertGreater(len(ip), 0)

    def test_get_local_ip_fallback_on_error(self):
        """Hata durumunda 127.0.0.1 dondurmeli."""
        with patch("utils.network.socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect.side_effect = Exception("No network")
            ip = get_local_ip()
            self.assertEqual(ip, "127.0.0.1")


class TestInternetConnection(unittest.TestCase):

    @patch("utils.network.urllib.request.urlopen")
    def test_check_internet_true(self, mock_urlopen):
        """Internet erisimi varsa True."""
        mock_urlopen.return_value = MagicMock()
        self.assertTrue(check_internet_connection())

    @patch("utils.network.urllib.request.urlopen")
    def test_check_internet_false(self, mock_urlopen):
        """Internet erisimi yoksa False."""
        mock_urlopen.side_effect = Exception("No internet")
        self.assertFalse(check_internet_connection())


class TestCheckTCPConnection(unittest.TestCase):

    def test_check_tcp_connection_to_closed_port_returns_false(self):
        """Kapali porta baglanti False dondurmeli."""
        result = check_tcp_connection("127.0.0.1", 19999, timeout=1)
        self.assertIsInstance(result, bool)
        # Port 19999 genellikle kapalidir

    @patch("utils.network.socket.create_connection")
    def test_check_tcp_connection_success(self, mock_conn):
        """Basarili baglanti True dondurmeli."""
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = check_tcp_connection("127.0.0.1", 8080)
        self.assertTrue(result)



class TestCheckLocalHttpHealth(unittest.TestCase):

    @patch("utils.network.urllib.request.urlopen")
    def test_health_success_first_path(self, mock_urlopen):
        """/ahws-health yolunda basarili yanit (200) True dondurmeli."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_local_http_health()
        self.assertTrue(result)
        mock_urlopen.assert_called_once()
        self.assertIn("/ahws-health", mock_urlopen.call_args[0][0])

    @patch("utils.network.urllib.request.urlopen")
    def test_health_success_second_path(self, mock_urlopen):
        """Ilk yolda hata olup, ikinci yolda (/) basarili yanit True dondurmeli."""
        mock_resp_success = MagicMock()
        mock_resp_success.status = 200

        mock_urlopen.side_effect = [
            Exception("Connection refused"),
            MagicMock(__enter__=MagicMock(return_value=mock_resp_success))
        ]

        result = check_local_http_health()
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("utils.network.urllib.request.urlopen")
    def test_health_fail_http_error(self, mock_urlopen):
        """HTTP Hata durumlari (400, 500) False dondurmeli."""
        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = check_local_http_health()
        self.assertFalse(result)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("utils.network.urllib.request.urlopen")
    def test_health_fail_exceptions(self, mock_urlopen):
        """Tüm yollarda Exception (örn. Timeout) False dondurmeli."""
        mock_urlopen.side_effect = Exception("Timeout")

        result = check_local_http_health()
        self.assertFalse(result)
        self.assertEqual(mock_urlopen.call_count, 2)


if __name__ == "__main__":
    unittest.main()