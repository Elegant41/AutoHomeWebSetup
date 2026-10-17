"""
InstallerEngine birim testleri.
Tum servis cagrilari mock'lanir - admin veya internet gerektirmez.
"""
import queue
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.installer import InstallerEngine
from core.models import InstallConfig, NodeRole, ProgressEvent


class TestInstallerEngineInit(unittest.TestCase):
    """InstallerEngine baslangic testleri."""

    def test_default_init(self):
        """InstallerEngine varsayilan baslangic degerleri dogru olmali."""
        engine = InstallerEngine()
        self.assertIsNotNone(engine.progress_queue)
        self.assertFalse(engine.is_running())
        self.assertIsNotNone(engine.downloader)
        self.assertIsNotNone(engine.caddy_service)
        self.assertIsNotNone(engine.cloudflare_service)
        self.assertIsNotNone(engine.syncthing_service)

    def test_custom_queue(self):
        """Ozel queue ile baslatma."""
        q = queue.Queue()
        engine = InstallerEngine(progress_queue=q)
        self.assertIs(engine.progress_queue, q)

    def test_is_not_running_initially(self):
        """Baslangicta is_running() False olmali."""
        engine = InstallerEngine()
        self.assertFalse(engine.is_running())


class TestInstallerEngineEmit(unittest.TestCase):
    """InstallerEngine emit metodlari testleri."""

    def setUp(self):
        self.q = queue.Queue()
        self.engine = InstallerEngine(progress_queue=self.q)

    def test_emit_sends_progress_event(self):
        """_emit() kuyruğa ProgressEvent gönderir."""
        self.engine._emit("Test mesaj", 50)
        event = self.q.get_nowait()
        self.assertEqual(event.message, "Test mesaj")
        self.assertEqual(event.percentage, 50)
        self.assertFalse(event.is_error)
        self.assertFalse(event.is_complete)
        self.assertFalse(event.is_cancelled)

    def test_emit_error(self):
        """_emit_error() is_error=True olan event gonderir."""
        self.engine._emit_error("Hata olustu")
        event = self.q.get_nowait()
        self.assertTrue(event.is_error)
        self.assertEqual(event.message, "Hata olustu")

    def test_emit_complete(self):
        """_emit_complete() is_complete=True olan event gonderir."""
        self.engine._emit_complete()
        event = self.q.get_nowait()
        self.assertTrue(event.is_complete)
        self.assertEqual(event.percentage, 100)

    def test_emit_cancelled(self):
        """_emit_cancelled() is_cancelled=True olan event gonderir."""
        self.engine._emit_cancelled()
        event = self.q.get_nowait()
        self.assertTrue(event.is_cancelled)


class TestInstallerEngineCancel(unittest.TestCase):
    """InstallerEngine iptal mekanizmasi testleri."""

    def test_cancel_sets_event(self):
        """cancel() cagrisi _cancel_event'i set eder."""
        engine = InstallerEngine()
        self.assertFalse(engine._cancel_event.is_set())
        engine.cancel()
        self.assertTrue(engine._cancel_event.is_set())


class TestInstallerEngineRollback(unittest.TestCase):
    """InstallerEngine rollback testleri."""

    def test_rollback_calls_uninstall_in_reverse(self):
        """
        _rollback() tamamlanan adimlari ters sirayla kaldirir.
        caddy -> cloudflared -> syncthing kurulmussa
        rollback: syncthing -> cloudflared -> caddy
        """
        engine = InstallerEngine()
        call_order = []

        engine.caddy_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("caddy_uninstall"))
        engine.cloudflare_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("cloudflare_uninstall"))
        engine.syncthing_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("syncthing_uninstall"))

        engine._completed_steps = ["caddy", "cloudflared", "syncthing"]
        engine._rollback()

        self.assertEqual(call_order,
                         ["syncthing_uninstall", "cloudflare_uninstall", "caddy_uninstall"])

    def test_rollback_partial_steps(self):
        """Sadece ilk adim tamamlanmissa yalnizca o geri alinir."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock()
        engine.cloudflare_service.uninstall = MagicMock()

        engine._completed_steps = ["caddy"]
        engine._rollback()

        engine.caddy_service.uninstall.assert_called_once()
        engine.cloudflare_service.uninstall.assert_not_called()

    def test_rollback_error_does_not_propagate(self):
        """Rollback sirasinda olusan hata yakalanir, yayilmaz."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock(
            side_effect=Exception("Servis kaldirilmadi"))

        engine._completed_steps = ["caddy"]
        try:
            engine._rollback()
        except Exception:
            self.fail("_rollback() exception yaymamali")

    def test_rollback_clears_completed_steps(self):
        """Rollback sonrasi _completed_steps bos olmali."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock()
        engine._completed_steps = ["caddy"]
        engine._rollback()
        self.assertEqual(engine._completed_steps, [])


class TestInstallerProgressCallback(unittest.TestCase):
    """Progress callback yuzde esleme testleri."""

    def setUp(self):
        self.q = queue.Queue()
        self.engine = InstallerEngine(progress_queue=self.q)

    def _drain(self):
        """Queue'yu bosalt, son eventi dondur."""
        event = None
        while not self.q.empty():
            event = self.q.get_nowait()
        return event

    def test_caddy_callback_range_start(self):
        """Caddy progress %10-%35 araligina eslenmeli."""
        self.engine._caddy_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertIsNotNone(event)
        self.assertGreaterEqual(event.percentage, 10)
        self.assertLessEqual(event.percentage, 35)

    def test_caddy_callback_range_end(self):
        """Caddy %100 icin de aralik icinde olmali."""
        self.engine._caddy_progress_callback(100, "Bitti")
        event = self._drain()
        self.assertIsNotNone(event)
        self.assertGreaterEqual(event.percentage, 10)
        self.assertLessEqual(event.percentage, 35)

    def test_cloudflared_callback_range(self):
        """Cloudflared progress %35-%60 araligina eslenmeli."""
        self.engine._cloudflared_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertGreaterEqual(event.percentage, 35)
        self.assertLessEqual(event.percentage, 60)

    def test_syncthing_callback_range(self):
        """Syncthing progress %60-%83 araligina eslenmeli."""
        self.engine._syncthing_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertGreaterEqual(event.percentage, 60)
        self.assertLessEqual(event.percentage, 83)

    def test_negative_percent_not_emitted(self):
        """Negatif yuzde emit edilmemeli."""
        self.engine._caddy_progress_callback(-1, "Hata")
        self.assertTrue(self.q.empty(), "Negatif yuzde event gonderilmemeli")


class TestInstallerFixesAndImprovements(unittest.TestCase):
    """Yeni eklenen duzeltme ve iyilestirmelerin birim testleri."""

    def test_handle_cancel_triggers_rollback_and_cancelled_event(self):
        """Iptal istendiginde tamamlanan adimlar geri alinmali ve cancelled eventi gonderilmeli."""
        q = queue.Queue()
        engine = InstallerEngine(progress_queue=q)
        engine.caddy_service.uninstall = MagicMock()
        engine._completed_steps = ["caddy"]
        engine.cancel()

        cancelled = engine._handle_cancel_if_requested()
        self.assertTrue(cancelled)
        engine.caddy_service.uninstall.assert_called_once()
        events = []
        while not q.empty():
            events.append(q.get_nowait())
        self.assertTrue(any(e.is_cancelled for e in events))

    def test_setup_secondary_node_shares_exact_site_root_path(self):
        """Yedek dugum kurulumunda Syncthing klasoru tam olarak config.site_root_path ile paylasilmali."""
        import shutil
        import tempfile

        temp_site = Path(tempfile.mkdtemp())
        try:
            engine = InstallerEngine()
            engine.syncthing_service.add_device = MagicMock()
            engine.syncthing_service.share_folder = MagicMock()

            cfg = InstallConfig(
                site_root_path=str(temp_site),
                node_role=NodeRole.SECONDARY,
                primary_device_id="AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
            )
            engine._setup_secondary_node(cfg)

            engine.syncthing_service.add_device.assert_called_once_with(
                device_id=cfg.primary_device_id,
                name="Merkez Sunucu",
                auto_accept=True,
            )
            engine.syncthing_service.share_folder.assert_called_once_with(
                folder_id="auto-home-web",
                folder_path=str(temp_site),
                device_ids=[cfg.primary_device_id],
                label="AHWS Web Site",
            )
        finally:
            shutil.rmtree(temp_site, ignore_errors=True)

    def test_uninstall_all_removes_services_and_config(self):
        """uninstall_all() tum servisleri kaldirmali ve konfigurasyonu silmeli."""
        engine = InstallerEngine()
        engine.syncthing_service.uninstall = MagicMock()
        engine.cloudflare_service.uninstall = MagicMock()
        engine.caddy_service.uninstall = MagicMock()
        engine.config_manager.delete = MagicMock()

        engine.uninstall_all()

        engine.syncthing_service.uninstall.assert_called_once()
        engine.cloudflare_service.uninstall.assert_called_once()
        engine.caddy_service.uninstall.assert_called_once()
        engine.config_manager.delete.assert_called_once()

    def test_get_system_health_returns_connected_and_paired_devices(self):
        """get_system_health() hem eslesmis hem de aktif bagli dugum sayisini dondurmeli."""
        engine = InstallerEngine()
        local_id = "LOCAL11-LOCAL11-LOCAL11-LOCAL11-LOCAL11-LOCAL11-LOCAL11-LOCAL11"
        remote_id = "REMOTE2-REMOTE2-REMOTE2-REMOTE2-REMOTE2-REMOTE2-REMOTE2-REMOTE2"

        engine.config_manager.load = MagicMock(return_value={"caddy_port": 80})
        engine.caddy_service.is_running = MagicMock(return_value=True)
        engine.cloudflare_service.is_running = MagicMock(return_value=True)
        engine.syncthing_service.is_running = MagicMock(return_value=True)
        engine.syncthing_service.sync_credentials_from_config = MagicMock()
        engine.syncthing_service.get_device_id = MagicMock(return_value=local_id)
        engine.syncthing_service.get_devices = MagicMock(return_value=[
            {"deviceID": local_id, "name": "Local"},
            {"deviceID": remote_id, "name": "Remote"},
        ])
        engine.syncthing_service.get_connections = MagicMock(return_value={
            remote_id: {"connected": True}
        })

        health = engine.get_system_health()
        self.assertTrue(health["caddy_running"])
        self.assertTrue(health["cloudflared_running"])
        self.assertTrue(health["syncthing_running"])
        self.assertEqual(health["paired_devices"], 1)
        self.assertEqual(health["connected_devices"], 1)

    def test_add_secondary_node_uses_auto_accept_and_saves_config(self):
        """add_secondary_node() auto_accept=True ile cihaz eklemeli ve klasoru paylasmali."""
        engine = InstallerEngine()
        sec_id = "SECOND2-SECOND2-SECOND2-SECOND2-SECOND2-SECOND2-SECOND2-SECOND2"

        engine.syncthing_service.sync_credentials_from_config = MagicMock()
        engine.syncthing_service.is_api_ready = MagicMock(return_value=True)
        engine.syncthing_service.add_device = MagicMock()
        engine.syncthing_service.share_folder = MagicMock()
        engine.config_manager.load = MagicMock(return_value={"site_root_path": "C:/test_site"})
        engine.config_manager.save = MagicMock()

        engine.add_secondary_node(sec_id, "Yedek-1")

        engine.syncthing_service.add_device.assert_called_once_with(
            sec_id,
            "Yedek-1",
            auto_accept=True,
        )
        engine.syncthing_service.share_folder.assert_called_once_with(
            folder_id="auto-home-web",
            folder_path="C:/test_site",
            device_ids=[sec_id],
            label="AHWS Web Site",
        )
        engine.config_manager.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()