"""
Uygulama konfigürasyon yönetimi.

install_config.json dosyasının kaydedilmesi, yüklenmesi ve
rollback bilgilerinin saklanması.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from utils import constants
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Kurulum konfigürasyon dosyası yönetimi.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (constants.CONFIG_DIR / "install_config.json")
        self.legacy_config_path = Path(r"C:\ProgramData\AutoHomeWebSetup\config\install_config.json")

    def _ensure_migrated(self) -> None:
        """Eski AutoHomeWebSetup konfigürasyonunu yeni AHWS dizinine kopyalar/taşır."""
        try:
            if not self.config_path.exists() and self.legacy_config_path.exists():
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(self.legacy_config_path, self.config_path)
                logger.info(f"Eski konfigürasyon taşındı: {self.legacy_config_path} -> {self.config_path}")
        except Exception as e:
            logger.warning(f"Konfigürasyon taşıma uyarısı: {e}")

    def save(
        self,
        data: dict[str, Any],
        include_metadata: bool = True,
    ) -> Path:
        """
        Konfigürasyonu JSON dosyasına kaydeder.

        Args:
            data: Kaydedilecek konfigürasyon verisi
            include_metadata: Tarih vb. meta veriyi ekle

        Returns:
            Path: Kaydedilen dosya yolu
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        save_data = dict(data)

        if include_metadata:
            save_data["install_date"] = datetime.now().isoformat()

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Konfigürasyon kaydedildi: {self.config_path}")
        return self.config_path

    def load(self) -> dict[str, Any]:
        """
        Konfigürasyonu yükler.

        Returns:
            dict: Yüklenen konfigürasyon (bulunamazsa boş dict)

        Raises:
            json.JSONDecodeError: Dosya bozuksa
        """
        self._ensure_migrated()
        target = self.config_path if self.config_path.exists() else self.legacy_config_path
        if not target.exists():
            logger.warning(f"Konfigürasyon dosyası bulunamadı: {self.config_path}")
            return {}

        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Konfigürasyon yüklendi: {target}")
        return data

    def exists(self) -> bool:
        """Konfigürasyon dosyasının var olup olmadığını kontrol eder."""
        self._ensure_migrated()
        return self.config_path.exists() or self.legacy_config_path.exists()

    def delete(self) -> None:
        """Konfigürasyon dosyasını siler."""
        if self.config_path.exists():
            self.config_path.unlink()
            logger.info(f"Konfigürasyon silindi: {self.config_path}")
        if self.legacy_config_path.exists():
            try:
                self.legacy_config_path.unlink()
            except Exception:
                pass

    def get_installed_services(self) -> list[str]:
        """Kurulu servislerin listesini döndürür."""
        data = self.load()
        return data.get("installed_services", [])

    def update_installed_services(self, services: list[str]) -> None:
        """Kurulu servisler listesini günceller."""
        data = self.load()
        data["installed_services"] = services
        self.save(data, include_metadata=False)

    def get_created_directories(self) -> list[str]:
        """Oluşturulan dizinlerin listesini döndürür."""
        data = self.load()
        return data.get("created_directories", [])

    def update_created_directories(self, directories: list[str]) -> None:
        """Oluşturulan dizinler listesini günceller."""
        data = self.load()
        data["created_directories"] = directories
        self.save(data, include_metadata=False)

    def get_syncthing_config(self) -> dict[str, Any]:
        """Syncthing için kaydedilmiş konfigürasyonu döndürür."""
        data = self.load()
        return data.get("syncthing", {})

    def update_syncthing_config(self, syncthing_data: dict[str, Any]) -> None:
        """Syncthing konfigürasyonunu günceller."""
        data = self.load()
        data["syncthing"] = syncthing_data
        self.save(data, include_metadata=False)