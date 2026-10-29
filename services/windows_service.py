"""
Windows Servis Yönetimi.

SC (Service Control) ve NSSM (Non-Sucking Service Manager) ile
Windows servislerini oluşturma, başlatma, durdurma, silme işlemleri.
"""

import subprocess
from pathlib import Path
from typing import Optional

from utils import constants
from utils.logger import get_logger
from utils.platform_utils import is_valid_binary, run_command

logger = get_logger(__name__)

# CREATE_NO_WINDOW flag
CREATE_NO_WINDOW = 0x08000000


class ServiceError(Exception):
    """Windows servis işlemlerinde oluşan hatalar için özel istisna."""

    pass


class SCService:
    """
    Windows Service Control (sc.exe) yardımcıları.
    """

    @classmethod
    def _get_service_names(cls, name: str) -> list[str]:
        names = [name]
        if name.startswith("AHWS-"):
            names.append(name.replace("AHWS-", "AutoHomeWebSetup-"))
        elif name.startswith("AutoHomeWebSetup-"):
            names.append(name.replace("AutoHomeWebSetup-", "AHWS-"))
        return names

    @classmethod
    def is_installed(cls, name: str) -> bool:
        """Servisin kurulu olup olmadığını kontrol eder (eski ve yeni isimleri destekler)."""
        for sname in cls._get_service_names(name):
            result = run_command(["sc", "query", sname])
            if result.returncode == 0:
                return True
        return False

    @classmethod
    def is_running(cls, name: str) -> bool:
        """Servisin çalışıp çalışmadığını kontrol eder (eski ve yeni isimleri destekler)."""
        for sname in cls._get_service_names(name):
            result = run_command(["sc", "query", sname])
            if result.returncode == 0 and "RUNNING" in result.stdout.upper():
                return True
        return False

    @classmethod
    def query(cls, name: str) -> dict:
        """
        Servisin durumunu sorgular.

        Returns:
            dict: Servis durum bilgisi
        """
        is_inst = cls.is_installed(name)
        is_run = cls.is_running(name)
        return {
            "name": name,
            "is_installed": is_inst,
            "is_running": is_run,
            "raw_output": "",
        }

    @staticmethod
    def create(
        name: str,
        bin_path: str,
        display_name: str = "",
        description: str = "",
        start_type: str = "auto",
    ) -> None:
        """
        Windows servisi oluşturur.

        Args:
            name: Servis adı
            bin_path: Çalıştırılacak exe/dizin yolu
            display_name: Görünen ad
            description: Açıklama
            start_type: Başlatma tipi (auto, manual, disabled)

        Raises:
            ServiceError: Servis oluşturulamazsa
        """
        cmd = ["sc", "create", name, f"binPath={bin_path}", f"start={start_type}"]

        if display_name:
            cmd.append(f"DisplayName={display_name}")

        result = run_command(cmd)

        if result.returncode != 0:
            error_msg = f"Servis oluşturulamadı ({name}): {result.stderr.strip() or result.stdout.strip()}"
            raise ServiceError(error_msg)

        if description:
            SCService.set_description(name, description)

        logger.info(f"Servis oluşturuldu: {name} ({bin_path})")

    @staticmethod
    def set_description(name: str, description: str) -> None:
        """Servis açıklamasını ayarlar."""
        run_command(["sc", "description", name, description])

    @staticmethod
    def start(name: str, wait_timeout: int = 10) -> None:
        """Servisi başlatır."""
        import time

        result = run_command(["sc", "start", name])
        stdout_str = result.stdout if isinstance(result.stdout, str) else ""
        stderr_str = result.stderr if isinstance(result.stderr, str) else ""
        output = (stderr_str + " " + stdout_str).strip()

        if result.returncode == 0 and "PENDING" not in output.upper():
            logger.info(f"Servis başlatıldı: {name}")
            return

        deadline = time.time() + wait_timeout
        while time.time() < deadline:
            if SCService.is_running(name):
                logger.info(f"Servis başlatıldı ve aktif: {name}")
                return
            time.sleep(0.1)

        if result.returncode != 0 and not SCService.is_running(name):
            raise ServiceError(f"Servis başlatılamadı ({name}): {output}")
        logger.info(f"Servis başlatıldı: {name}")

    @staticmethod
    def stop(name: str) -> None:
        """Servisi durdurur."""
        result = run_command(["sc", "stop", name])
        if result.returncode != 0 and "STOPPED" not in result.stdout.upper():
            raise ServiceError(f"Servis durdurulamadı ({name}): {result.stderr.strip() or result.stdout.strip()}")
        logger.info(f"Servis durduruldu: {name}")

    @staticmethod
    def restart(name: str, wait_timeout: int = 10) -> None:
        """Servisi yeniden başlatır."""
        try:
            SCService.stop(name)
        except ServiceError:
            pass
        import time
        time.sleep(0.5)
        SCService.start(name, wait_timeout=wait_timeout)

    @staticmethod
    def delete(name: str) -> None:
        """Servisi siler."""
        if not SCService.is_installed(name):
            return

        result = run_command(["sc", "delete", name])
        if result.returncode != 0:
            raise ServiceError(f"Servis silinemedi ({name}): {result.stderr.strip() or result.stdout.strip()}")
        logger.info(f"Servis silindi: {name}")


class NSSMService:
    """
    NSSM (Non-Sucking Service Manager) wrapper.

    NSSM, Caddy ve Syncthing gibi SCM (Service Control Manager)
    API sinyallerine yanıt vermeyen uygulamaları Windows servisi
    olarak çalıştırmak için kullanılır.
    """

    def __init__(self, nssm_path: Optional[str] = None):
        """
        Args:
            nssm_path: nssm.exe yolu (None ise varsayılan dizinden kullanılır)
        """
        self.nssm = nssm_path or str(constants.BIN_DIR / constants.NSSM_EXE)

    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        """NSSM komutunu çalıştırır."""
        nssm_path = Path(self.nssm)
        if nssm_path.exists() and not is_valid_binary(nssm_path):
            raise ServiceError(f"NSSM çalıştırılabilir dosyası geçersiz (0 bayt): {self.nssm}")
        cmd = [self.nssm] + args
        result = run_command(cmd)
        return result

    def is_installed(self, name: str) -> bool:
        """Servisin kurulu olup olmadığını kontrol eder."""
        return SCService.is_installed(name)

    def is_running(self, name: str) -> bool:
        """Servisin çalışıp çalışmadığını kontrol eder."""
        return SCService.is_running(name)

    def install(
        self,
        name: str,
        exe_path: str,
        arguments: str = "",
        display_name: str = "",
        description: str = "",
        app_directory: str = "",
    ) -> None:
        """
        NSSM ile Windows servisi kurar.

        Args:
            name: Servis adı
            exe_path: Çalıştırılacak exe yolu
            arguments: Program argümanları
            display_name: Görünen ad
            description: Açıklama
            app_directory: Çalışma dizini

        Raises:
            ServiceError: Servis kurulamazsa
        """
        # Servis zaten kuruluysa önce sil
        if self.is_installed(name):
            self.remove(name)

        # NSSM install
        result = self._run(["install", name, exe_path])
        if result.returncode != 0:
            raise ServiceError(
                f"NSSM servis kurulumu başarısız ({name}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )

        # Parametreleri ayarla
        if arguments:
            self.set_param(name, "AppParameters", arguments)

        if display_name:
            self.set_param(name, "DisplayName", display_name)

        if description:
            self.set_param(name, "Description", description)

        if app_directory:
            self.set_param(name, "AppDirectory", app_directory)

        # Log ayarları
        self.set_param(name, "AppStdout", str(constants.LOGS_DIR / f"{name}.log"))
        self.set_param(name, "AppStderr", str(constants.LOGS_DIR / f"{name}.log"))
        self.set_param(name, "AppRotateFiles", "1")
        self.set_param(name, "AppRotateBytes", "10485760")  # 10 MB

        logger.info(f"NSSM servis kuruldu: {name} ({exe_path} {arguments})")

    def set_param(self, name: str, param: str, value: str) -> None:
        """NSSM servis parametresini ayarlar."""
        result = self._run(["set", name, param, value])
        if result.returncode != 0:
            raise ServiceError(
                f"NSSM parametresi ayarlanamadı ({name}.{param}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )

    def start(self, name: str, wait_timeout: int = 10) -> None:
        """Servisi başlatır."""
        import time

        result = self._run(["start", name])
        stdout_str = result.stdout if isinstance(result.stdout, str) else ""
        stderr_str = result.stderr if isinstance(result.stderr, str) else ""
        output = (stderr_str + " " + stdout_str).strip()

        if result.returncode == 0 and "PENDING" not in output.upper():
            logger.info(f"NSSM servis başlatıldı: {name}")
            return

        deadline = time.time() + wait_timeout
        while time.time() < deadline:
            if SCService.is_running(name):
                logger.info(f"NSSM servis başlatıldı ve aktif: {name}")
                return
            time.sleep(0.1)

        if result.returncode != 0 and not SCService.is_running(name):
            raise ServiceError(
                f"NSSM servis başlatılamadı ({name}): {output}"
            )
        logger.info(f"NSSM servis başlatıldı: {name}")

    def stop(self, name: str) -> None:
        """Servisi durdurur."""
        if not self.is_installed(name):
            return

        result = self._run(["stop", name])
        if result.returncode != 0:
            raise ServiceError(
                f"NSSM servis durdurulamadı ({name}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        logger.info(f"NSSM servis durduruldu: {name}")

    def restart(self, name: str, wait_timeout: int = 10) -> None:
        """Servisi yeniden başlatır."""
        try:
            self.stop(name)
        except ServiceError:
            pass
        import time
        time.sleep(0.5)
        self.start(name, wait_timeout=wait_timeout)

    def remove(self, name: str) -> None:
        """Servisi kaldırır."""
        if not self.is_installed(name):
            return

        # Önce durdur (çalışıyorsa)
        try:
            self.stop(name)
        except ServiceError:
            pass

        result = self._run(["remove", name, "confirm"])
        if result.returncode != 0:
            raise ServiceError(
                f"NSSM servis kaldırılamadı ({name}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        logger.info(f"NSSM servis kaldırıldı: {name}")


# ─── Yardımcı Fonksiyonlar ───────────────────────────────────────────
def is_service_installed(name: str) -> bool:
    """Bir servisin kurulu olup olmadığını kontrol eder."""
    return SCService.is_installed(name)


def is_service_running(name: str) -> bool:
    """Bir servisin çalışıp çalışmadığını kontrol eder."""
    return SCService.is_running(name)