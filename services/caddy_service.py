"""
Caddy Servis Entegrasyonu.

Caddy web sunucusunun kurulumu, Caddyfile oluşturma ve
NSSM ile Windows servisi olarak kaydedilmesi.
"""

from pathlib import Path
from typing import Optional

from core.downloader import Downloader
from services.windows_service import NSSMService, ServiceError
from utils import constants
from utils.logger import get_logger
from utils.platform_utils import add_firewall_rule, is_valid_binary, remove_firewall_rule

logger = get_logger(__name__)


class CaddyService:
    """
    Caddy web sunucusu yönetimi.
    """

    def __init__(self, downloader: Optional[Downloader] = None):
        self.downloader = downloader or Downloader()
        self.nssm = NSSMService()
        self.install_dir = constants.INSTALL_DIR
        self.bin_dir = constants.BIN_DIR

    def is_installed(self) -> bool:
        """Caddy servisinin kurulu olup olmadığını kontrol eder."""
        return self.nssm.is_installed(constants.SERVICE_CADDY)

    def is_running(self) -> bool:
        """Caddy servisinin çalışıp çalışmadığını kontrol eder."""
        return self.nssm.is_running(constants.SERVICE_CADDY)

    def generate_caddyfile(
        self,
        site_root: str,
        port: int = constants.CADDY_DEFAULT_PORT,
        log_path: Optional[Path] = None,
    ) -> Path:
        """
        Caddyfile oluşturur ve kaydeder.

        Args:
            site_root: Statik site dosyalarının kök dizini
            port: Dinlenecek port (varsayılan: 80)
            log_path: Caddy log dosyası yolu

        Returns:
            Path: Oluşturulan Caddyfile yolu
        """
        log_path = log_path or constants.LOGS_DIR / "caddy.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        site_root_clean = str(Path(site_root).resolve()).replace("\\", "/")
        log_path_clean = str(Path(log_path).resolve()).replace("\\", "/")

        # Caddyfile şablonu (/ahws-health sağlık kontrolü dahil)
        caddyfile_content = f""":{port} {{
    root * "{site_root_clean}"
    handle /ahws-health {{
        respond "OK" 200
    }}
    file_server
    encode gzip
    log {{
        output file "{log_path_clean}"
    }}
}}
"""

        # HATA-08: Caddyfile'ı SADECE config dizinine yaz, site_root'a değil
        config_caddyfile = constants.CADDYFILE_PATH
        config_caddyfile.parent.mkdir(parents=True, exist_ok=True)
        config_caddyfile.write_text(caddyfile_content, encoding="utf-8")

        logger.info(f"Caddyfile oluşturuldu: {config_caddyfile}")
        return config_caddyfile

    def create_caddyfile(
        self,
        site_root_or_port: str | int,
        port_or_site_root: int | str = constants.CADDY_DEFAULT_PORT,
        log_path: Optional[Path] = None,
    ) -> Path:
        """
        generate_caddyfile için geriye dönük uyumlu yardımcı metot.
        Hem (site_root, port) hem de (port, site_root) parametre sırasını destekler.
        """
        if isinstance(site_root_or_port, int) and isinstance(port_or_site_root, str):
            return self.generate_caddyfile(port_or_site_root, site_root_or_port, log_path=log_path)
        return self.generate_caddyfile(str(site_root_or_port), int(port_or_site_root), log_path=log_path)

    def cleanup_existing_caddy(self) -> None:
        """Önceki Caddy servisini ve artık çalışan caddy.exe süreçlerini temizler."""
        logger.info("Önceki Caddy servis ve süreçleri temizleniyor...")
        try:
            if self.is_installed():
                self.uninstall()
        except Exception as e:
            logger.warning(f"Önceki Caddy servisi kaldırılırken uyarı: {e}")

        try:
            from utils.platform_utils import run_command
            run_command(["taskkill", "/F", "/IM", "caddy.exe"])
        except Exception:
            pass

    def install(
        self,
        site_root: str,
        port: int = constants.CADDY_DEFAULT_PORT,
        progress_callback=None,
    ) -> Path:
        """
        Caddy'yi indirir, Caddyfile oluşturur ve NSSM servisi olarak kurar.

        Args:
            site_root: Statik site dosyalarının kök dizini
            port: Dinlenecek port
            progress_callback: İlerleme geri çağrısı (yüzde, mesaj)

        Returns:
            Path: Caddy binary yolu

        Raises:
            ServiceError: Servis kurulamazsa
        """
        try:
            # Önceki kalan caddy servis veya süreçlerini temizle
            self.cleanup_existing_caddy()

            # 1. Caddy binary'sini indir
            if progress_callback:
                progress_callback(10, "Caddy indiriliyor...")

            caddy_exe = self.bin_dir / constants.CADDY_EXE
            if not is_valid_binary(caddy_exe):
                caddy_exe = self.downloader.download_caddy(progress_callback)
            else:
                logger.info(f"Caddy zaten mevcut: {caddy_exe}")
                if progress_callback:
                    progress_callback(100, "Caddy zaten mevcut")

            # Güvenlik duvarı izni ekle
            add_firewall_rule(constants.FIREWALL_RULE_CADDY, str(caddy_exe))

            # 2. Caddyfile oluştur
            if progress_callback:
                progress_callback(40, "Caddyfile oluşturuluyor...")

            caddyfile_path = self.generate_caddyfile(site_root, port)
            caddyfile_clean = str(Path(caddyfile_path).resolve()).replace("\\", "/")

            # 3. NSSM servisi olarak kur
            if progress_callback:
                progress_callback(60, "Caddy servisi kaydediliyor...")

            log_path = constants.LOGS_DIR / "caddy.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)

            self.nssm.install(
                name=constants.SERVICE_CADDY,
                exe_path=str(caddy_exe),
                arguments=f'run --config "{caddyfile_clean}" --adapter caddyfile',
                display_name="AHWS Caddy Web Server",
                description="Caddy statik web sunucusu (AHWS tarafından yönetilir)",
                app_directory=str(self.bin_dir),
            )

            # 4. Servisi başlat
            if progress_callback:
                progress_callback(80, "Caddy servisi başlatılıyor...")

            self.nssm.start(constants.SERVICE_CADDY)

            if progress_callback:
                progress_callback(100, "Caddy kurulumu tamamlandı")

            logger.info(f"Caddy servisi kuruldu ve başlatıldı (port: {port})")
            return caddy_exe

        except Exception as e:
            if not isinstance(e, ServiceError):
                raise ServiceError(f"Caddy kurulum hatası: {e}") from e
            raise

    def restart(self) -> None:
        """Caddy servisini yeniden başlatır."""
        self.nssm.restart(constants.SERVICE_CADDY)

    def uninstall(self) -> None:
        """Caddy servisini durdurur ve kaldırır."""
        logger.info("Caddy servisi kaldırılıyor...")
        self.nssm.remove(constants.SERVICE_CADDY)
        remove_firewall_rule(constants.FIREWALL_RULE_CADDY)
        logger.info("Caddy servisi kaldırıldı")

    def get_status(self) -> dict:
        """Caddy servisinin durumunu döndürür."""
        return {
            "name": constants.SERVICE_CADDY,
            "is_installed": self.is_installed(),
            "is_running": self.is_running(),
        }