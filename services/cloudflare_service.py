"""
Cloudflared Servis Entegrasyonu.

Cloudflare Tunnel connector'ının kurulumu ve servis kaydı.
Cloudflared kendi Windows servisini oluşturur (NSSM gerekmez).
"""

import re
from pathlib import Path
from typing import Optional

from core.downloader import Downloader
from services.windows_service import SCService, ServiceError
from utils import constants
from utils.logger import get_logger
from utils.platform_utils import is_valid_binary, run_command

logger = get_logger(__name__)


class CloudflareService:
    """
    Cloudflared Tunnel yönetimi.
    """

    def __init__(self, downloader: Optional[Downloader] = None):
        self.downloader = downloader or Downloader()
        self.install_dir = constants.INSTALL_DIR
        self.bin_dir = constants.BIN_DIR

    def is_installed(self) -> bool:
        """Cloudflared servisinin kurulu olup olmadığını kontrol eder."""
        return SCService.is_installed(constants.SERVICE_CLOUDFLARED)

    def is_running(self) -> bool:
        """Cloudflared servisinin çalışıp çalışmadığını kontrol eder."""
        return SCService.is_running(constants.SERVICE_CLOUDFLARED)

    def validate_token(self, token: str) -> bool:
        """
        Cloudflare Tunnel token formatını doğrular.

        Args:
            token: Cloudflare Tunnel token

        Returns:
            bool: Token formatı geçerliyse True
        """
        if not token:
            return False
        return bool(re.match(constants.CLOUDFLARE_TOKEN_REGEX, token))

    def _download_binary(self, progress_callback=None) -> Path:
        """Cloudflared binary'sini indirir veya mevcut olanı döndürür."""
        if progress_callback:
            progress_callback(10, "Cloudflared indiriliyor...")

        cloudflared_exe = self.bin_dir / constants.CLOUDFLARED_EXE
        if not is_valid_binary(cloudflared_exe):
            cloudflared_exe = self.downloader.download_cloudflared(progress_callback)
        else:
            logger.info(f"Cloudflared zaten mevcut: {cloudflared_exe}")
            if progress_callback:
                progress_callback(100, "Cloudflared zaten mevcut")

        return cloudflared_exe

    def _register_service(self, cloudflared_exe: Path, token: str, progress_callback=None) -> None:
        """Cloudflared servisini kaydeder."""
        if self.is_installed():
            logger.info("Cloudflared servisi zaten kurulu, yeniden kuruluyor...")
            self.uninstall()

        if progress_callback:
            progress_callback(50, "Cloudflared servisi kuruluyor...")

        result = run_command(
            [str(cloudflared_exe), "service", "install", token],
            timeout=60,
        )

        if result.returncode != 0:
            raise ServiceError(
                f"Cloudflared servis kurulumu başarısız: "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )

    def _start_service(self, progress_callback=None) -> None:
        """Cloudflared servisini başlatır."""
        if progress_callback:
            progress_callback(80, "Cloudflared servisi başlatılıyor...")

        SCService.start(constants.SERVICE_CLOUDFLARED)

        if progress_callback:
            progress_callback(100, "Cloudflared kurulumu tamamlandı")

        logger.info("Cloudflared servisi kuruldu ve başlatıldı")

    def install(
        self,
        token: str,
        progress_callback=None,
    ) -> Path:
        """
        Cloudflared'ı indirir ve servis olarak kurar.

        Args:
            token: Cloudflare Tunnel token
            progress_callback: İlerleme geri çağrısı (yüzde, mesaj)

        Returns:
            Path: cloudflared.exe yolu

        Raises:
            ServiceError: Kurulum başarısız olursa
        """
        try:
            # Token doğrulama
            if not self.validate_token(token):
                raise ServiceError("Geçersiz Cloudflare Tunnel token formatı.")

            # 1. Cloudflared binary'sini indir
            cloudflared_exe = self._download_binary(progress_callback)

            # 2 & 3. Servis zaten kuruluysa kaldır ve yenisini kur
            self._register_service(cloudflared_exe, token, progress_callback)

            # 4. Servisi başlat
            self._start_service(progress_callback)

            return cloudflared_exe

        except Exception as e:
            if not isinstance(e, ServiceError):
                raise ServiceError(f"Cloudflared kurulum hatası: {e}") from e
            raise

    def restart(self) -> None:
        """Cloudflared servisini yeniden başlatır."""
        SCService.restart(constants.SERVICE_CLOUDFLARED)

    def uninstall(self) -> None:
        """Cloudflared servisini kaldırır."""
        logger.info("Cloudflared servisi kaldırılıyor...")

        # Servisi durdur
        if self.is_running():
            try:
                SCService.stop(constants.SERVICE_CLOUDFLARED)
            except ServiceError:
                pass

        cloudflared_exe = self.bin_dir / constants.CLOUDFLARED_EXE
        if cloudflared_exe.exists():
            result = run_command(
                [str(cloudflared_exe), "service", "uninstall"],
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning(
                    f"cloudflared service uninstall uyarısı, sc delete deneniyor: "
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )
                if self.is_installed():
                    SCService.delete(constants.SERVICE_CLOUDFLARED)
        else:
            logger.warning("cloudflared.exe bulunamadı, sc delete ile servis kaldırılıyor")
            if self.is_installed():
                SCService.delete(constants.SERVICE_CLOUDFLARED)

        logger.info("Cloudflared servisi kaldırıldı")

    def get_status(self) -> dict:
        """Cloudflared servisinin durumunu döndürür."""
        return {
            "name": constants.SERVICE_CLOUDFLARED,
            "is_installed": self.is_installed(),
            "is_running": self.is_running(),
        }