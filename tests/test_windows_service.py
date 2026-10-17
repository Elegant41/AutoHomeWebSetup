"""
Windows Service modülü birim testleri.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.windows_service import SCService, NSSMService, ServiceError

import unittest


class TestSCService(unittest.TestCase):
    """SCService sınıfı testleri."""

    @patch("services.windows_service.run_command")
    def test_is_installed_true(self, mock_run):
        """Kurulu servis kontrolü testi."""
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(SCService.is_installed("TestService"))

    @patch("services.windows_service.run_command")
    def test_is_installed_false(self, mock_run):
        """Kurulu olmayan servis kontrolü testi."""
        mock_run.return_value = MagicMock(returncode=1060)
        self.assertFalse(SCService.is_installed("TestService"))

    @patch("services.windows_service.run_command")
    def test_is_running(self, mock_run):
        """Çalışan servis kontrolü testi."""
        mock_run.return_value = MagicMock(returncode=0, stdout="STATE              : 4  RUNNING")
        self.assertTrue(SCService.is_running("TestService"))

    @patch("services.windows_service.run_command")
    def test_create_success(self, mock_run):
        """Servis oluşturma testi."""
        mock_run.return_value = MagicMock(returncode=0)
        SCService.create("TestService", "C:/test.exe")
        mock_run.assert_called()

    @patch("services.windows_service.run_command")
    def test_create_failure(self, mock_run):
        """Servis oluşturma hatası testi."""
        mock_run.return_value = MagicMock(returncode=5, stderr="Access denied")
        with self.assertRaises(ServiceError):
            SCService.create("TestService", "C:/test.exe")


class TestNSSMService(unittest.TestCase):
    """NSSMService sınıfı testleri."""

    def setUp(self):
        self.nssm = NSSMService("C:/nssm.exe")

    @patch("services.windows_service.run_command")
    def test_install_success(self, mock_run):
        """NSSM servis kurulum testi."""
        mock_run.return_value = MagicMock(returncode=0)

        # is_installed check
        with patch.object(SCService, "is_installed", return_value=False):
            self.nssm.install("TestService", "C:/app.exe", "run")
            # HATA-11: install(1) + AppParameters(1) + log ayarlari(4) = 6
            self.assertEqual(mock_run.call_count, 6)

    @patch("services.windows_service.run_command")
    def test_start_success(self, mock_run):
        """NSSM servis başlatma testi."""
        mock_run.return_value = MagicMock(returncode=0)
        self.nssm.start("TestService")
        mock_run.assert_called_with(["C:/nssm.exe", "start", "TestService"])

    @patch.object(SCService, "is_running", return_value=False)
    @patch("services.windows_service.run_command")
    def test_start_failure(self, mock_run, _mock_running):
        """NSSM servis başlatma hatası testi."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Failed")
        with self.assertRaises(ServiceError):
            self.nssm.start("TestService", wait_timeout=0)

    @patch.object(NSSMService, "start")
    @patch.object(NSSMService, "stop")
    def test_restart(self, mock_stop, mock_start):
        """NSSM servis yeniden başlatma testi."""
        self.nssm.restart("TestService")
        mock_stop.assert_called_once_with("TestService")
        mock_start.assert_called_once_with("TestService", wait_timeout=10)


if __name__ == "__main__":
    unittest.main()