"""
Kurulum Motoru (InstallerEngine).

Tüm kurulum adımlarını orkestra eder. Worker thread'de çalışır ve
GUI'ye thread-safe queue üzerinden ilerleme olayları gönderir.
Hata durumunda rollback mekanizmasını tetikler.
"""

import queue
import threading
from pathlib import Path
from typing import Callable, Optional

from core.config_manager import ConfigManager
from core.downloader import DownloadCancelledError, Downloader
from core.models import InstallConfig, NodeRole, ProgressEvent
from services.caddy_service import CaddyService
from services.cloudflare_service import CloudflareService
from services.syncthing_service import SyncthingService
from utils import constants
from utils.i18n import t
from utils.logger import get_logger
from utils.network import check_local_http_health
from utils.platform_utils import create_app_directories, disable_sleep_on_ac

logger = get_logger(__name__)


class InstallerEngine:
    """
    Ana kurulum orkestratörü.

    Uzun süren işlemler arka plan thread'inde çalışır. GUI, progress_queue'yu
    poll ederek canlı ilerlemeyi gösterir.
    """

    def __init__(
        self,
        progress_queue: Optional[queue.Queue] = None,
        config_manager: Optional[ConfigManager] = None,
    ):
        """
        Args:
            progress_queue: ProgressEvent nesnelerinin gönderileceği thread-safe queue
            config_manager: Konfigürasyon yöneticisi
        """
        self.progress_queue = progress_queue or queue.Queue()
        self.config_manager = config_manager or ConfigManager()

        self._worker_thread: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()
        self._is_running = False
        self._completed_steps: list[str] = []

        # Servis referansları
        self.downloader = Downloader(cancel_event=self._cancel_event)
        self.caddy_service = CaddyService(self.downloader)
        self.cloudflare_service = CloudflareService(self.downloader)
        self.syncthing_service = SyncthingService(self.downloader)

    # ─── Thread Yönetimi ────────────────────────────────────────────
    def start(self, config: InstallConfig) -> None:
        """
        Kurulumu başlatır (worker thread'de).

        Args:
            config: Kurulum yapılandırması
        """
        if self._is_running:
            logger.warning("Kurulum zaten çalışıyor")
            return

        self._cancel_event.clear()
        self._is_running = True
        self._completed_steps = []

        self._worker_thread = threading.Thread(
            target=self._run_installation,
            args=(config,),
            daemon=True,  # Ana uygulama kapanınca thread de kapanır
            name="InstallerThread",
        )
        self._worker_thread.start()
        logger.info("Kurulum thread'i başlatıldı")

    def cancel(self) -> None:
        """Kurulumu iptal etmek için sinyal gönderir."""
        self._cancel_event.set()
        logger.info("Kurulum iptal sinyali gönderildi")

    def is_running(self) -> bool:
        """Kurulumun çalışıp çalışmadığını döndürür."""
        return self._is_running

    def wait(self, timeout: Optional[float] = None) -> None:
        """Worker thread'in bitmesini bekler."""
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout)

    # ─── İlerleme Olayları ──────────────────────────────────────────
    def _emit(self, message: str, percentage: int) -> None:
        """GUI'ye ilerleme olayı gönderir."""
        self.progress_queue.put(ProgressEvent(message, percentage))

    def _emit_error(self, message: str) -> None:
        """GUI'ye hata olayı gönderir."""
        self.progress_queue.put(ProgressEvent(message, -1, is_error=True))

    def _emit_complete(self) -> None:
        """GUI'ye tamamlanma olayı gönderir."""
        self.progress_queue.put(
            ProgressEvent(t("step_complete"), 100, is_complete=True)
        )

    def _emit_cancelled(self) -> None:
        """GUI'ye iptal olayı gönderir."""
        self.progress_queue.put(
            ProgressEvent(t("step_cancel"), 0, is_cancelled=True)
        )

    def _handle_cancel_if_requested(self) -> bool:
        """İptal sinyali varsa yapılan adımları geri alır ve iptal olayı yayınlar."""
        if self._cancel_event.is_set():
            if self._completed_steps:
                self._rollback()
            self._emit_cancelled()
            return True
        return False

    # ─── Kurulum Akışı ──────────────────────────────────────────────
    def _run_installation(self, config: InstallConfig) -> None:
        """
        Worker thread'de çalışan ana kurulum akışı.

        Args:
            config: Kurulum yapılandırması
        """
        try:
            # Uygulama dizinlerini oluştur
            create_app_directories()
            self._emit(t("step_dirs"), 5)

            # Yedek düğümde site_root_path boşsa varsayılan SITE_DIR kullan
            if not config.site_root_path:
                config.site_root_path = str(constants.SITE_DIR)
            Path(config.site_root_path).mkdir(parents=True, exist_ok=True)

            # 1. NSSM'yi hazırla (Tüm servisler NSSM kullanır, en başta kurulmalıdır)
            if self._handle_cancel_if_requested():
                return

            self._emit(t("step_nssm"), 7)
            self.downloader.setup_nssm()

            # 2. Caddy kurulumu
            if self._handle_cancel_if_requested():
                return

            self._emit(t("step_caddy"), 10)
            self.caddy_service.install(
                site_root=config.site_root_path,
                port=config.caddy_port,
                progress_callback=self._caddy_progress_callback,
            )
            self._completed_steps.append("caddy")

            # 3. Cloudflared kurulumu
            if self._handle_cancel_if_requested():
                return

            self._emit(t("step_cf"), 35)
            self.cloudflare_service.install(
                token=config.cloudflare_token,
                progress_callback=self._cloudflared_progress_callback,
            )
            self._completed_steps.append("cloudflared")

            # 4. Syncthing kurulumu
            if self._handle_cancel_if_requested():
                return

            self._emit(t("step_sync"), 60)
            self.syncthing_service.install_as_service(
                progress_callback=self._syncthing_progress_callback,
                default_folder_path=config.site_root_path,
            )
            self._completed_steps.append("syncthing")

            # 5. Syncthing Device ID al
            if self._handle_cancel_if_requested():
                return

            self._emit(t("step_device_id"), 85)
            device_id = self.syncthing_service.get_device_id()
            config.local_device_id = device_id
            config.syncthing_api_key = self.syncthing_service.api_key
            config.syncthing_gui_port = self.syncthing_service.gui_port

            # 6. Yedek (secondary) ise cihaz eşleştirme, Merkez ise klasör paylaşımı
            if config.node_role == NodeRole.SECONDARY:
                self._setup_secondary_node(config)
            else:
                self._setup_primary_node(config)

            # 7. Güç / Uyku modu optimizasyonu (opsiyonel)
            if getattr(config, "prevent_sleep", True):
                disable_sleep_on_ac()

            # 8. Konfigürasyonu kaydet
            self._save_install_config(config)

            # 9. Tamamla
            self._emit_complete()
            self._is_running = False
            logger.info("Kurulum başarıyla tamamlandı")

        except DownloadCancelledError:
            logger.info("Kurulum indirme sırasında kullanıcı tarafından iptal edildi")
            self._rollback()
            self._emit_cancelled()
            self._is_running = False

        except Exception as e:
            logger.exception(f"Kurulum hatası: {e}")
            self._rollback()
            self._emit_error(str(e))
            self._is_running = False

        finally:
            self._is_running = False

    # ─── Node Kurulumları ───────────────────────────────────────────
    def _setup_primary_node(self, config: InstallConfig) -> None:
        """
        Merkez düğüm senkronizasyon hazırlığı.

        Site klasörünü Syncthing'de paylaşılabilir hale getirir.
        """
        self._emit(t("step_primary"), 88)

        folder_id = "auto-home-web"
        label = "AHWS Web Site"

        try:
            self.syncthing_service.share_folder(
                folder_id=folder_id,
                folder_path=config.site_root_path,
                device_ids=[],  # Cihazlar daha sonra "Yedek Ekle" ile eklenecek
                label=label,
            )
            logger.info("Merkez site klasörü Syncthing'de paylaşıldı")
        except Exception as e:
            logger.warning(f"Site klasörü paylaşılamadı: {e}")

        config.syncthing_api_key = self.syncthing_service.api_key
        config.syncthing_gui_port = self.syncthing_service.gui_port

    def _setup_secondary_node(self, config: InstallConfig) -> None:
        """
        Yedek düğüm kurulumu.

        Merkez cihazını Syncthing'e ekler, otomatik klasör kabulünü aktifleştirir
        ve Caddy'nin sunduğu site_root_path dizinini "auto-home-web" klasör ID'siyle
        Merkez cihaza bağlar.
        """
        self._emit(t("step_secondary"), 88)

        if not config.primary_device_id:
            raise ValueError("Yedek düğüm için merkez Device ID'si zorunludur.")

        # Yedek site dizinini hazırla
        target_site_dir = Path(config.site_root_path or constants.SITE_DIR)
        target_site_dir.mkdir(parents=True, exist_ok=True)
        config.site_root_path = str(target_site_dir)

        # 1. Merkez cihazını ekle (autoAcceptFolders: True)
        self.syncthing_service.add_device(
            device_id=config.primary_device_id,
            name="Merkez Sunucu",
            auto_accept=True,
        )

        self._emit(t("step_auto_accept"), 90)

        # 2. Aynı klasör ID'sini ("auto-home-web") Caddy'nin sunduğu dizinle eşleştir
        try:
            self.syncthing_service.share_folder(
                folder_id="auto-home-web",
                folder_path=config.site_root_path,
                device_ids=[config.primary_device_id],
                label="AHWS Web Site",
            )
        except Exception as e:
            logger.warning(f"Yedek düğüm klasör eşleştirme uyarısı: {e}")

        logger.info(f"Yedek düğüm hazırlandı (merkez cihazı eklendi, dizin: {config.site_root_path})")

    # ─── Progress Callback'ler ──────────────────────────────────────
    def _caddy_progress_callback(self, percent: int, message: str) -> None:
        """Caddy ilerleme callback'i."""
        if 0 <= percent <= 100:
            mapped = 10 + int(percent * 0.25)  # %10-35 aralığına eşle
            self._emit(message, mapped)

    def _cloudflared_progress_callback(self, percent: int, message: str) -> None:
        """Cloudflared ilerleme callback'i."""
        if 0 <= percent <= 100:
            mapped = 35 + int(percent * 0.25)  # %35-60 aralığına eşle
            self._emit(message, mapped)

    def _syncthing_progress_callback(self, percent: int, message: str) -> None:
        """Syncthing ilerleme callback'i."""
        if 0 <= percent <= 100:
            mapped = 60 + int(percent * 0.23)  # %60-83 aralığına eşle
            self._emit(message, mapped)

    # ─── Konfigürasyon Kaydı ────────────────────────────────────────
    def _save_install_config(self, config: InstallConfig) -> None:
        """
        Kurulum konfigürasyonunu install_config.json dosyasına kaydeder.

        Rollback ve uninstaller desteği için tüm parametreler saklanır.
        """
        data = config.to_dict()
        data.update({
            "installed_services": [
                constants.SERVICE_CADDY,
                constants.SERVICE_CLOUDFLARED,
                constants.SERVICE_SYNCTHING,
            ],
            "created_directories": [
                str(constants.INSTALL_DIR),
                str(constants.BIN_DIR),
                str(constants.CONFIG_DIR),
                str(constants.LOGS_DIR),
                str(constants.SITE_DIR),
            ],
            "node_role": config.node_role.value,
            "syncthing": {
                "api_key": config.syncthing_api_key,
                "gui_port": config.syncthing_gui_port,
            },
        })

        self.config_manager.save(data)
        logger.info("Kurulum konfigürasyonu kaydedildi")

    # ─── Rollback ve Kaldırma Mekanizması ───────────────────────────
    def _rollback(self) -> None:
        """
        Tamamlanan adımları ters sırada geri alır.

        Hata durumunda sistem tutarlı duruma getirilir.
        """
        logger.warning("Rollback başlatılıyor...")
        self._emit(t("step_rollback"), -1)

        for step in reversed(self._completed_steps):
            try:
                if step == "caddy":
                    logger.info("Caddy servisi kaldırılıyor (rollback)...")
                    self.caddy_service.uninstall()

                elif step == "cloudflared":
                    logger.info("Cloudflared servisi kaldırılıyor (rollback)...")
                    self.cloudflare_service.uninstall()

                elif step == "syncthing":
                    logger.info("Syncthing servisi kaldırılıyor (rollback)...")
                    self.syncthing_service.uninstall()

            except Exception as e:
                logger.warning(f"Rollback hatası ({step}): {e}")

        self._completed_steps.clear()
        logger.info("Rollback tamamlandı")

    def uninstall_all(self) -> None:
        """
        Kurulu tüm AHWS servislerini (Caddy, Cloudflared, Syncthing) ve
        yapılandırma dosyalarını kaldırır.
        """
        logger.info("Tüm AHWS servisleri ve yapılandırması kaldırılıyor...")
        errors: list[str] = []

        for name, svc in (
            ("Syncthing", self.syncthing_service),
            ("Cloudflared", self.cloudflare_service),
            ("Caddy", self.caddy_service),
        ):
            try:
                svc.uninstall()
            except Exception as e:
                logger.warning(f"{name} kaldırılırken uyarı: {e}")
                errors.append(f"{name}: {e}")

        try:
            if constants.CADDYFILE_PATH.exists():
                constants.CADDYFILE_PATH.unlink()
        except Exception:
            pass

        try:
            self.config_manager.delete()
        except Exception as e:
            logger.warning(f"Konfigürasyon silinirken uyarı: {e}")

        if errors:
            raise RuntimeError("\n".join(errors))

        logger.info("Tüm servisler ve yapılandırma başarıyla kaldırıldı")

    def get_system_health(self) -> dict:
        """
        Tüm servislerin ve yerel web sunucusunun canlı sağlık durumunu döndürür.
        """
        config_data = {}
        try:
            config_data = self.config_manager.load()
        except Exception:
            pass

        port = config_data.get("caddy_port", constants.CADDY_DEFAULT_PORT)
        caddy_running = self.caddy_service.is_running()
        cf_running = self.cloudflare_service.is_running()
        st_running = self.syncthing_service.is_running()
        http_ok = check_local_http_health(port) if caddy_running else False

        paired_devices = 0
        connected_devices = 0
        if st_running:
            try:
                self.syncthing_service.sync_credentials_from_config()
                try:
                    local_id = self.syncthing_service.get_device_id()
                except Exception:
                    local_id = config_data.get("local_device_id", "")

                devices = self.syncthing_service.get_devices()
                remote_ids = [
                    d.get("deviceID")
                    for d in devices
                    if d.get("deviceID") and d.get("deviceID") != local_id
                ]
                paired_devices = len(remote_ids)

                if paired_devices > 0:
                    conns = self.syncthing_service.get_connections()
                    connected_devices = sum(
                        1 for rid in remote_ids
                        if isinstance(conns.get(rid), dict) and conns[rid].get("connected") is True
                    )
            except Exception:
                pass

        return {
            "caddy_running": caddy_running,
            "cloudflared_running": cf_running,
            "syncthing_running": st_running,
            "http_ok": http_ok,
            "paired_devices": paired_devices,
            "connected_devices": connected_devices,
            "caddy_port": port,
        }

    # ─── Node Yönetimi (GUI'den çağrılır) ───────────────────────────
    def add_secondary_node(self, device_id: str, name: str = "") -> None:
        """
        Mevcut kuruluma yeni bir yedek düğüm ekler.

        Merkez bilgisayardan, kurulum tamamlandıktan sonra çağrılır.

        Args:
            device_id: Yedek bilgisayarın Syncthing Device ID'si
            name: Yedek düğüm için görünen ad
        """
        config_data = self.config_manager.load()
        syncthing_data = config_data.get("syncthing", {})

        # Önce config.xml'den güncel kimlik bilgilerini senkronize et
        self.syncthing_service.sync_credentials_from_config()

        api_key = (
            self.syncthing_service.api_key
            or config_data.get("syncthing_api_key", "")
            or syncthing_data.get("api_key", "")
        )
        gui_port = (
            self.syncthing_service.gui_port
            or config_data.get("syncthing_gui_port", 0)
            or syncthing_data.get("gui_port", 0)
            or constants.SYNCTHING_API_PORT
        )

        self.syncthing_service.api_key = api_key
        self.syncthing_service.gui_port = gui_port
        self.syncthing_service.api_base = f"http://127.0.0.1:{gui_port}"
        self.syncthing_service._headers["X-API-Key"] = api_key

        # Cihazı ekle (karşılıklı klasör paylaşımının takılmaması için auto_accept=True)
        self.syncthing_service.add_device(device_id, name or "Yedek Düğüm", auto_accept=True)

        # Site klasörünü paylaş
        site_root = config_data.get("site_root_path", "")
        if not site_root:
            try:
                for f in self.syncthing_service.get_folders():
                    if f.get("id") == "auto-home-web" and f.get("path"):
                        site_root = f["path"]
                        break
            except Exception:
                pass
        if not site_root:
            site_root = str(constants.SITE_DIR)

        self.syncthing_service.share_folder(
            folder_id="auto-home-web",
            folder_path=site_root,
            device_ids=[device_id],
            label="AHWS Web Site",
        )

        try:
            sec_ids = list(config_data.get("secondary_device_ids", []))
            if device_id not in sec_ids:
                sec_ids.append(device_id)
            config_data["secondary_device_ids"] = sec_ids
            self.config_manager.save(config_data)
        except Exception:
            pass

        logger.info(f"Yedek düğüm eklendi: {device_id[:12]}...")