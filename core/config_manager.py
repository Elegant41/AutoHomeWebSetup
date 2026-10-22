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

    def _decrypt_legacy_token(self, data: dict[str, Any], target_path: Path) -> bool:
        """
        Eski AHWS sürümlerinden kalan Fernet ile şifrelenmiş Cloudflare token'ı çözer.
        Token başarıyla çözülürse True döner ve data sözlüğü güncellenir.
        """
        token = data.get("cloudflare_token")
        is_encrypted = data.get("_is_encrypted", False)

        if not token or not isinstance(token, str):
            if "_is_encrypted" in data:
                data.pop("_is_encrypted", None)
            return False

        token_str = token.strip()
        # Eğer token zaten eyJ... ile başlıyorsa ve şifreli değilse müdahale etme
        if token_str.startswith("eyJ") and not is_encrypted:
            return False

        # Fernet şifreli metinler genelde 'gAAAAAB' ile başlar veya _is_encrypted bayrağı vardır
        if not is_encrypted and not token_str.startswith("gAAAAAB"):
            return False

        possible_keys = [
            self.config_path.parent / "secret.key",
            target_path.parent / "secret.key",
            self.legacy_config_path.parent / "secret.key",
            Path(r"C:\ProgramData\AHWS\config\secret.key"),
            Path(r"C:\ProgramData\AutoHomeWebSetup\config\secret.key"),
        ]

        fernet_key: Optional[bytes] = None
        for kpath in possible_keys:
            if kpath.exists():
                try:
                    with open(kpath, "rb") as kf:
                        content = kf.read().strip()
                        if content:
                            fernet_key = content
                            break
                except Exception as e:
                    logger.debug(f"Anahtar okuma hatası ({kpath}): {e}")

        if not fernet_key:
            logger.warning("Şifreli token tespit edildi ancak secret.key bulunamadı.")
            return False

        try:
            from cryptography.fernet import Fernet

            f = Fernet(fernet_key)
            decrypted = f.decrypt(token_str.encode("utf-8")).decode("utf-8").strip()
            if decrypted.startswith("eyJ"):
                data["cloudflare_token"] = decrypted
                data.pop("_is_encrypted", None)
                logger.info("Eski Fernet şifreli Cloudflare token'ı başarıyla çözüldü.")
                return True
            else:
                logger.warning("Token çözüldü fakat beklenen 'eyJ' ile başlamıyor.")
        except Exception as e:
            logger.warning(f"Fernet token çözme hatası: {e}")

        return False

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
        save_data.pop("_is_encrypted", None)

        if "cloudflare_token" in save_data and isinstance(save_data["cloudflare_token"], str):
            save_data["cloudflare_token"] = save_data["cloudflare_token"].strip()

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

        if self._decrypt_legacy_token(data, target):
            try:
                self.save(data, include_metadata=False)
            except Exception as e:
                logger.warning(f"Düzeltilen konfigürasyon diske kaydedilemedi: {e}")

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
