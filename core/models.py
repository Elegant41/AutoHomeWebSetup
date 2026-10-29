"""
Veri modelleri.

Sihirbaz boyunca toplanan kullanıcı girişleri, kurulum durumu ve
ilerleme olayları için dataclass tanımları.
"""

import base64
import json
import zlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from utils import constants


class NodeRole(Enum):
    """Düğüm rolü: Merkez veya Yedek."""

    PRIMARY = "primary"  # Merkez bilgisayar
    SECONDARY = "secondary"  # Yedek bilgisayar (Node)


@dataclass
class InstallConfig:
    """
    Sihirbaz boyunca toplanan tüm kullanıcı girişleri.
    """

    # Sayfa 2: Sunucu Ayarları
    site_root_path: str = ""
    cloudflare_token: str = ""
    public_domain: str = ""
    prevent_sleep: bool = True

    # Sayfa 3: Senkronizasyon Ayarları
    node_role: NodeRole = NodeRole.PRIMARY
    primary_device_id: str = ""  # Sadece SECONDARY rolünde gerekli

    # Otomatik doldurulacaklar
    install_dir: str = str(constants.INSTALL_DIR)
    caddy_port: int = constants.CADDY_DEFAULT_PORT
    syncthing_gui_port: int = constants.SYNCTHING_GUI_PORT
    syncthing_api_key: str = ""  # Otomatik üretilecek
    local_device_id: str = ""  # Kurulum sonrası Syncthing'den alınacak

    def to_dict(self) -> dict[str, Any]:
        """Konfigürasyonu sözlük olarak döndürür."""
        return {
            "site_root_path": self.site_root_path,
            "cloudflare_token": self.cloudflare_token,
            "public_domain": self.public_domain,
            "prevent_sleep": self.prevent_sleep,
            "node_role": self.node_role.value,
            "primary_device_id": self.primary_device_id,
            "install_dir": self.install_dir,
            "caddy_port": self.caddy_port,
            "syncthing_gui_port": self.syncthing_gui_port,
            "syncthing_api_key": self.syncthing_api_key,
            "local_device_id": self.local_device_id,
        }

    @staticmethod
    def _process_cloudflare_token(token: str) -> str:
        """Cloudflare token'ını temizler ve gerekiyorsa eski şifrelemeyi çözer."""
        if not token or not isinstance(token, str):
            return token
        token = constants.clean_cloudflare_token(token.strip())
        if token.startswith("gAAAAAB"):
            try:
                from core.config_manager import ConfigManager
                cfg = ConfigManager()
                dummy = {"cloudflare_token": token, "_is_encrypted": True}
                if cfg._decrypt_legacy_token(dummy, cfg.config_path):
                    return dummy.get("cloudflare_token", token)
            except Exception:
                pass
        return token

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InstallConfig":
        """Sözlükten InstallConfig oluşturur."""
        config = cls()
        config.site_root_path = data.get("site_root_path", "")
        config.cloudflare_token = cls._process_cloudflare_token(data.get("cloudflare_token", ""))
        config.public_domain = data.get("public_domain", "")
        config.prevent_sleep = data.get("prevent_sleep", True)
        role = data.get("node_role", "primary")
        config.node_role = NodeRole(role) if role in ("primary", "secondary") else NodeRole.PRIMARY
        config.primary_device_id = data.get("primary_device_id", "")
        config.install_dir = data.get("install_dir", str(constants.INSTALL_DIR))
        config.caddy_port = data.get("caddy_port", constants.CADDY_DEFAULT_PORT)
        config.syncthing_gui_port = data.get("syncthing_gui_port", constants.SYNCTHING_GUI_PORT)
        config.syncthing_api_key = data.get("syncthing_api_key", "")
        config.local_device_id = data.get("local_device_id", "")
        return config

    @staticmethod
    def generate_join_key(
        cloudflare_token: str,
        primary_device_id: str,
        caddy_port: int = constants.CADDY_DEFAULT_PORT,
        public_domain: str = "",
    ) -> str:
        """
        Yedek düğümlerin tek kodla kurulabilmesi için Küme Katılım Kodu (Join Key) üretir.
        """
        if not cloudflare_token or not primary_device_id:
            return ""

        token_to_use = InstallConfig._process_cloudflare_token(cloudflare_token)

        payload = {
            "t": token_to_use,
            "d": primary_device_id.strip(),
            "p": int(caddy_port),
            "u": public_domain.strip(),
        }
        raw_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        compressed = zlib.compress(raw_bytes, level=9)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
        return f"{constants.JOIN_KEY_PREFIX}{encoded}"

    @staticmethod
    def parse_join_key(join_key: str) -> Optional[dict[str, Any]]:
        """
        Küme Katılım Kodunu (AHWS1-...) çözümler.
        Geçersizse None döndürür.
        """
        if not join_key:
            return None
        cleaned = join_key.strip()
        if not cleaned.startswith(constants.JOIN_KEY_PREFIX):
            return None
        b64_part = cleaned[len(constants.JOIN_KEY_PREFIX):]
        if not b64_part:
            return None
        # Base64 padding tamamla
        padding = (4 - len(b64_part) % 4) % 4
        b64_padded = b64_part + ("=" * padding)
        try:
            compressed = base64.urlsafe_b64decode(b64_padded.encode("ascii"))
            raw_bytes = zlib.decompress(compressed)
            payload = json.loads(raw_bytes.decode("utf-8"))
            if not isinstance(payload, dict):
                return None

            raw_token = str(payload.get("t", "")).strip()
            token = InstallConfig._process_cloudflare_token(raw_token)

            device_id = str(payload.get("d", "")).strip()
            port = int(payload.get("p", constants.CADDY_DEFAULT_PORT))
            domain = str(payload.get("u", "")).strip()

            if not token or not device_id:
                return None

            return {
                "cloudflare_token": token,
                "primary_device_id": device_id,
                "caddy_port": port,
                "public_domain": domain,
            }
        except Exception:
            return None


@dataclass
class ProgressEvent:
    """
    Kurulum ilerleme olayı. Worker thread'den GUI'ye gönderilir.
    """

    message: str
    percentage: int
    is_error: bool = False
    is_complete: bool = False
    is_cancelled: bool = False


@dataclass
class ServiceStatus:
    """Bir servisin mevcut durumu."""

    name: str
    is_installed: bool = False
    is_running: bool = False
    error: Optional[str] = None


@dataclass
class InstallResult:
    """
    Kurulum sonucu. InstallerEngine tarafından döndürülür.
    """

    success: bool
    message: str
    device_id: str = ""
    rollback_performed: bool = False
    completed_steps: list[str] = field(default_factory=list)
