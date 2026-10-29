"""
Syncthing Servis Entegrasyonu.

Syncthing kurulumu, ilk yapılandırma üretimi, NSSM ile Windows
servisi oluşturma, REST API yönetimi ve cihaz eşleştirme.
"""

import random
import time
from pathlib import Path
from typing import Optional

import requests

from core.downloader import Downloader
from services.windows_service import NSSMService, ServiceError
from utils import constants
from utils.logger import get_logger
from utils.network import find_available_port, is_port_available
from utils.platform_utils import (
    add_firewall_rule,
    is_valid_binary,
    remove_firewall_rule,
)

logger = get_logger(__name__)


class SyncthingService:
    """
    Syncthing dosya senkronizasyon yönetimi.
    """

    def __init__(
        self,
        downloader: Optional[Downloader] = None,
        api_key: str = "",
        gui_port: int = constants.SYNCTHING_API_PORT,
    ):
        self.downloader = downloader or Downloader()
        self.nssm = NSSMService()
        self.install_dir = constants.INSTALL_DIR
        self.bin_dir = constants.BIN_DIR
        self.home_dir = constants.SYNCTHING_HOME_DIR

        self.api_key = api_key or self._generate_api_key()
        self.gui_port = gui_port
        self.api_base = f"http://127.0.0.1:{self.gui_port}"

        self._headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        # Mevcut config.xml varsa API anahtarını ve portu oradan senkronize et
        if not api_key:
            self.sync_credentials_from_config()

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def _generate_api_key(
        self, length: int = constants.SYNCTHING_API_KEY_LENGTH
    ) -> str:
        """Rastgele bir API anahtarı üretir."""
        return "".join(
            random.SystemRandom().choice(constants.SYNCTHING_API_KEY_CHARS)
            for _ in range(length)
        )

    def is_installed(self) -> bool:
        """Syncthing servisinin kurulu olup olmadığını kontrol eder."""
        return self.nssm.is_installed(constants.SERVICE_SYNCTHING)

    def is_running(self) -> bool:
        """Syncthing servisinin çalışıp çalışmadığını kontrol eder."""
        return self.nssm.is_running(constants.SERVICE_SYNCTHING)

    def _read_api_key_from_config(self, config_path: Path) -> str:
        """config.xml dosyasından apikey değerini okur."""
        if not config_path.exists():
            return ""
        try:
            content = config_path.read_text(encoding="utf-8")
            import re

            match = re.search(r"<apikey>([^<]+)</apikey>", content)
            if match:
                return match.group(1).strip()
            match_attr = re.search(r'apikey="([^"]+)"', content)
            if match_attr:
                return match_attr.group(1).strip()
        except Exception:
            pass
        return ""

    def _read_gui_port_from_config(self, config_path: Path) -> int:
        """config.xml dosyasından GUI port değerini okur."""
        if not config_path.exists():
            return 0
        try:
            content = config_path.read_text(encoding="utf-8")
            import re

            match = re.search(
                r"<gui\b[^>]*>.*?<address>[^:<]+:(\d+)</address>", content, re.DOTALL
            )
            if match:
                return int(match.group(1))
        except Exception:
            pass
        return 0

    def sync_credentials_from_config(self) -> None:
        """Disk üzerinde mevcut bir config.xml varsa api_key ve gui_port bilgilerini yükler."""
        config_path = self.home_dir / "config.xml"
        if not config_path.exists():
            return
        real_key = self._read_api_key_from_config(config_path)
        if real_key:
            self.api_key = real_key
            self._headers["X-API-Key"] = real_key
        real_port = self._read_gui_port_from_config(config_path)
        if real_port > 0:
            self.gui_port = real_port
            self.api_base = f"http://127.0.0.1:{self.gui_port}"

    # ─── İlk Yapılandırma ───────────────────────────────────────────
    def generate_initial_config(
        self,
        home_dir: Optional[Path] = None,
        gui_port: Optional[int] = None,
        api_key: Optional[str] = None,
        default_folder_path: Optional[str] = None,
    ) -> Path:
        """
        Syncthing'in ilk yapılandırmasını üretir veya mevcut config.xml'i
        eşleşmiş cihazları ve klasörleri koruyarak günceller.

        Args:
            home_dir: Syncthing home dizini
            gui_port: GUI/API portu
            api_key: API anahtarı
            default_folder_path: Otomatik kabul edilen klasörler için varsayılan dizin

        Returns:
            Path: config.xml yolu
        """
        import xml.etree.ElementTree as ET

        home_dir = home_dir or self.home_dir
        gui_port = gui_port or constants.SYNCTHING_GUI_PORT
        api_key = api_key or self.api_key
        self.api_key = api_key
        self._headers["X-API-Key"] = api_key

        home_dir.mkdir(parents=True, exist_ok=True)
        config_path = home_dir / "config.xml"

        # Port çakışması kontrolü: hedef port meşgulse alternatif kullan
        if not is_port_available(gui_port, "127.0.0.1"):
            alt_port = find_available_port(constants.SYNCTHING_GUI_PORT_ALT)
            if alt_port > 0:
                gui_port = alt_port
                self.gui_port = gui_port
                self.api_base = f"http://127.0.0.1:{self.gui_port}"
                logger.info(
                    f"Syncthing portu çakışması, alternatif port kullanılıyor: {gui_port}"
                )
        else:
            self.gui_port = gui_port
            self.api_base = f"http://127.0.0.1:{self.gui_port}"

        default_dir = (
            Path(default_folder_path) if default_folder_path else constants.SITE_DIR
        )
        default_dir_clean = str(default_dir.resolve()).replace("\\", "/")

        # Eğer geçerli bir config.xml zaten varsa, cihaz ve klasörleri koruyarak güncelle
        if config_path.exists():
            try:
                tree = ET.parse(config_path)
                root = tree.getroot()
                if root.tag == "configuration":
                    gui_el = root.find("gui")
                    if gui_el is None:
                        gui_el = ET.SubElement(root, "gui")
                    gui_el.set("enabled", "true")
                    gui_el.set("tls", "false")

                    addr_el = gui_el.find("address")
                    if addr_el is None:
                        addr_el = ET.SubElement(gui_el, "address")
                    addr_el.text = f"127.0.0.1:{gui_port}"

                    key_el = gui_el.find("apikey")
                    if key_el is None:
                        key_el = ET.SubElement(gui_el, "apikey")
                    key_el.text = api_key

                    opts_el = root.find("options")
                    if opts_el is None:
                        opts_el = ET.SubElement(root, "options")
                    def_path_el = opts_el.find("defaultFolderPath")
                    if def_path_el is None:
                        def_path_el = ET.SubElement(opts_el, "defaultFolderPath")
                    def_path_el.text = default_dir_clean

                    defaults_el = root.find("defaults")
                    if defaults_el is not None:
                        def_folder = defaults_el.find("folder")
                        if def_folder is not None:
                            def_folder.set("path", default_dir_clean)

                    tree.write(config_path, encoding="utf-8", xml_declaration=True)
                    logger.info(
                        f"Mevcut Syncthing yapılandırması korunarak güncellendi: {config_path}"
                    )
                    return config_path
            except Exception as e:
                logger.warning(
                    f"Mevcut config.xml ayrıştırılamadı, sıfırdan oluşturuluyor: {e}"
                )

        # Modern Syncthing (v2.x - version 52) config.xml şablonu
        config_template = f"""<?xml version="1.0" encoding="utf-8"?>
<configuration version="52">
    <gui enabled="true" tls="false" debugging="false" sendBasicAuthPrompt="false" theme="default">
        <address>127.0.0.1:{gui_port}</address>
        <user></user>
        <password></password>
        <apikey>{api_key}</apikey>
        <insecureAdminAccess>false</insecureAdminAccess>
    </gui>
    <options>
        <globalAnnounceEnabled>true</globalAnnounceEnabled>
        <localAnnounceEnabled>true</localAnnounceEnabled>
        <relaysEnabled>true</relaysEnabled>
        <natEnabled>true</natEnabled>
        <urAccepted>-1</urAccepted>
        <autoUpgradeIntervalH>0</autoUpgradeIntervalH>
        <restartOnWakeup>true</restartOnWakeup>
        <defaultFolderPath>{default_dir_clean}</defaultFolderPath>
    </options>
    <defaults>
        <folder id="" label="" path="{default_dir_clean}" type="sendreceive" rescanIntervalS="60" fsWatcherEnabled="true" fsWatcherDelayS="10" ignorePerms="true" autoNormalize="true">
            <minDiskFree unit="%">1</minDiskFree>
        </folder>
    </defaults>
</configuration>
"""

        config_path.write_text(config_template, encoding="utf-8")
        logger.info(f"Syncthing ilk yapılandırma oluşturuldu: {config_path}")
        return config_path

    def cleanup_existing_syncthing(self) -> None:
        """Önceki Syncthing servisini ve artık çalışan syncthing.exe süreçlerini temizler."""
        logger.info("Önceki Syncthing servis ve süreçleri temizleniyor...")
        try:
            if self.is_installed():
                self.uninstall()
        except Exception as e:
            logger.warning(f"Önceki Syncthing servisi kaldırılırken uyarı: {e}")

        try:
            from utils.platform_utils import run_command

            run_command(["taskkill", "/F", "/IM", "syncthing.exe"])
            time.sleep(0.3)
        except Exception:
            pass

    # ─── Servis Kurulumu ────────────────────────────────────────────
    def _prepare_binary(self, progress_callback=None) -> Path:
        """Syncthing binary'sini hazırlar ve güvenlik duvarı iznini ekler."""
        if progress_callback:
            progress_callback(10, "Syncthing indiriliyor...")

        syncthing_exe = self.bin_dir / constants.SYNCTHING_EXE
        if not is_valid_binary(syncthing_exe):
            syncthing_exe = self.downloader.download_syncthing(progress_callback)
        else:
            logger.info(f"Syncthing zaten mevcut: {syncthing_exe}")
            if progress_callback:
                progress_callback(100, "Syncthing zaten mevcut")

        # Güvenlik duvarı izni ekle
        add_firewall_rule(constants.FIREWALL_RULE_SYNCTHING, str(syncthing_exe))
        return syncthing_exe

    def _setup_nssm_service(self, syncthing_exe: Path, progress_callback=None) -> None:
        """NSSM kullanarak Syncthing'i Windows servisi olarak kurar ve başlatır."""
        if progress_callback:
            progress_callback(60, "Syncthing servisi kaydediliyor...")

        home_dir_clean = str(Path(self.home_dir).resolve()).replace("\\", "/")
        arguments = (
            f"--no-browser --no-restart "
            f'--home="{home_dir_clean}" '
            f"--gui-address=127.0.0.1:{self.gui_port}"
        )

        self.nssm.install(
            name=constants.SERVICE_SYNCTHING,
            exe_path=str(syncthing_exe),
            arguments=arguments,
            display_name="AHWS Syncthing",
            description="Syncthing dosya senkronizasyonu (AHWS tarafından yönetilir)",
            app_directory=str(self.bin_dir),
        )

        # 4. Servisi başlat
        if progress_callback:
            progress_callback(80, "Syncthing servisi başlatılıyor...")

        self.nssm.start(constants.SERVICE_SYNCTHING)

    def install_as_service(
        self,
        progress_callback=None,
        default_folder_path: Optional[str] = None,
    ) -> Path:
        """
        Syncthing'i indirir ve NSSM ile Windows servisi olarak kurar.

        Args:
            progress_callback: İlerleme geri çağrısı (yüzde, mesaj)
            default_folder_path: Varsayılan senkronizasyon klasörü yolu

        Returns:
            Path: syncthing.exe yolu

        Raises:
            ServiceError: Kurulum başarısız olursa
        """
        try:
            self.cleanup_existing_syncthing()

            # 1. Binary hazırlık (indirme ve güvenlik duvarı)
            syncthing_exe = self._prepare_binary(progress_callback)

            # 2. İlk yapılandırmayı oluştur
            if progress_callback:
                progress_callback(30, "Syncthing yapılandırması oluşturuluyor...")
            self.generate_initial_config(default_folder_path=default_folder_path)

            # 3. NSSM servisini kur ve başlat
            self._setup_nssm_service(syncthing_exe, progress_callback)

            # 4. API'nin hazır olmasını bekle
            if progress_callback:
                progress_callback(90, "Syncthing API'si bekleniyor...")
            self.wait_for_api(timeout=constants.SYNCTHING_API_TIMEOUT)

            if progress_callback:
                progress_callback(100, "Syncthing kurulumu tamamlandı")

            logger.info(
                f"Syncthing servisi kuruldu ve başlatıldı (port: {self.gui_port})"
            )
            return syncthing_exe

        except Exception as e:
            if not isinstance(e, ServiceError):
                raise ServiceError(f"Syncthing kurulum hatası: {e}") from e
            raise

    # ─── API İletişimi ──────────────────────────────────────────────
    def wait_for_api(self, timeout: int = constants.SYNCTHING_API_TIMEOUT) -> bool:
        """
        Syncthing REST API'sinin erişilebilir olmasını bekler.

        Args:
            timeout: Maksimum bekleme süresi (saniye)

        Returns:
            bool: API erişilebilir ise True

        Raises:
            ServiceError: Süre aşımında
        """
        logger.info(f"Syncthing API bekleniyor (zaman aşımı: {timeout}s)...")
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                # config.xml'den güncel API key'i oku (Syncthing değiştirmişse senkronize ol)
                self.sync_credentials_from_config()

                response = requests.get(
                    f"{self.api_base}/rest/system/version",
                    headers=self._headers,
                    timeout=2,
                )
                if response.status_code == 200:
                    logger.info("Syncthing API hazır")
                    return True
            except requests.RequestException:
                pass

            time.sleep(constants.SYNCTHING_API_RETRY_INTERVAL)

        raise ServiceError(
            f"Syncthing API {timeout} saniye içinde erişilebilir olmadı. "
            f"Port: {self.gui_port}"
        )

    def get_device_id(self) -> str:
        """
        Bu cihazın Syncthing Device ID'sini alır.

        Returns:
            str: Device ID

        Raises:
            ServiceError: API isteği başarısız olursa
        """
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/system/status",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            device_id = response.json().get("myID", "")
            logger.info(f"Syncthing Device ID alındı: {device_id[:12]}...")
            return device_id
        except requests.RequestException as e:
            raise ServiceError(f"Syncthing Device ID alınamadı: {e}") from e

    def get_syncthing_version(self) -> str:
        """Syncthing sürümünü alır."""
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/system/version",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get("version", "")
        except requests.RequestException:
            return ""

    # ─── Cihaz Eşleştirme ───────────────────────────────────────────
    def get_devices(self) -> list[dict]:
        """
        Yapılandırılmış cihazları döndürür.

        HATA-01: API doğrudan list döndürür, dict değil.
        """
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/config/devices",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()  # API doğrudan list döndürür
        except requests.RequestException as e:
            raise ServiceError(f"Syncthing cihazlar alınamadı: {e}") from e

    def add_device(
        self,
        device_id: str,
        name: str = "",
        auto_accept: bool = False,
    ) -> None:
        """
        Syncthing'e yeni bir cihaz ekler.

        Args:
            device_id: Eklenecek cihazın Device ID'si
            name: Cihaz için görünen ad
            auto_accept: Cihazdan gelen klasör tekliflerini otomatik kabul et

        Raises:
            ServiceError: API isteği başarısız olursa
        """
        try:
            # Mevcut cihazları al
            devices = self.get_devices()

            # Cihaz zaten ekli mi?
            for device in devices:
                if device.get("deviceID") == device_id:
                    if auto_accept and not device.get("autoAcceptFolders"):
                        device["autoAcceptFolders"] = True
                        requests.put(
                            f"{self.api_base}/rest/config/devices",
                            headers=self._headers,
                            json=devices,
                            timeout=10,
                        ).raise_for_status()
                    logger.info(f"Cihaz zaten ekli: {device_id[:12]}...")
                    return

            # Yeni cihaz oluştur
            new_device = {
                "deviceID": device_id,
                "name": name or f"Yedek Düğüm {len(devices)}",
                "addresses": ["dynamic"],
                "compression": "metadata",
                "certName": "",
                "introducer": False,
                "skipIntroductionRemovals": False,
                "paused": False,
                "sharedFolders": [],
                "autoAcceptFolders": auto_accept,
                "maxSendKbps": 0,
                "maxRecvKbps": 0,
                "maxRequestKiB": 0,
                "untrusted": False,
                "remoteGUIAddress": "",
            }

            devices.append(new_device)

            # HATA-03: PUT payload direkt liste olmalı, dict değil
            response = requests.put(
                f"{self.api_base}/rest/config/devices",
                headers=self._headers,
                json=devices,  # Direkt liste gönder
                timeout=10,
            )
            response.raise_for_status()
            logger.info(
                f"Syncthing cihaz eklendi: {device_id[:12]}... ({name or 'İsimsiz'})"
            )

        except requests.RequestException as e:
            raise ServiceError(f"Syncthing cihaz eklenemedi: {e}") from e

    def remove_device(self, device_id: str) -> None:
        """
        Syncthing'den belirtilen cihazı ve klasör paylaşımlarındaki referansını kaldırır.
        """
        try:
            devices = self.get_devices()
            new_devices = [d for d in devices if d.get("deviceID") != device_id]
            if len(new_devices) != len(devices):
                requests.put(
                    f"{self.api_base}/rest/config/devices",
                    headers=self._headers,
                    json=new_devices,
                    timeout=10,
                ).raise_for_status()

            folders = self.get_folders()
            updated = False
            for folder in folders:
                orig_devs = folder.get("devices", [])
                filtered_devs = [d for d in orig_devs if d.get("deviceID") != device_id]
                if len(filtered_devs) != len(orig_devs):
                    folder["devices"] = filtered_devs
                    updated = True
            if updated:
                requests.put(
                    f"{self.api_base}/rest/config/folders",
                    headers=self._headers,
                    json=folders,
                    timeout=10,
                ).raise_for_status()

            logger.info(f"Syncthing cihaz kaldırıldı: {device_id[:12]}...")
        except requests.RequestException as e:
            raise ServiceError(f"Syncthing cihaz kaldırılamadı: {e}") from e

    # ─── Klasör Paylaşımı ───────────────────────────────────────────
    def get_folders(self) -> list[dict]:
        """
        Yapılandırılmış klasörleri döndürür.

        HATA-02: API doğrudan list döndürür, dict değil.
        """
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/config/folders",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()  # API doğrudan list döndürür
        except requests.RequestException as e:
            raise ServiceError(f"Syncthing klasörler alınamadı: {e}") from e

    def share_folder(
        self,
        folder_id: str,
        folder_path: str,
        device_ids: list[str],
        label: str = "",
    ) -> None:
        """
        Bir klasörü belirtilen cihazlarla paylaşır.

        Args:
            folder_id: Klasör kimliği
            folder_path: Klasörün disk üzerindeki yolu
            device_ids: Paylaşılacak cihazların ID'leri
            label: Klasör için görünen ad

        Raises:
            ServiceError: API isteği başarısız olursa
        """
        try:
            # Mevcut klasörleri al
            folders = self.get_folders()

            # Klasör zaten var mı?
            existing = None
            for folder in folders:
                if folder.get("id") == folder_id:
                    existing = folder
                    break

            if existing:
                # HATA-05: Mevcut klasöre cihazları dict formatında ekle ve yolu güncelle
                if folder_path:
                    existing["path"] = folder_path
                existing_device_ids = {
                    d["deviceID"] for d in existing.get("devices", [])
                }
                for dev_id in device_ids:
                    if dev_id not in existing_device_ids:
                        existing["devices"].append(
                            {"deviceID": dev_id, "encryptionPassword": ""}
                        )

                response = requests.put(
                    f"{self.api_base}/rest/config/folders/{folder_id}",
                    headers=self._headers,
                    json=existing,
                    timeout=10,
                )
                response.raise_for_status()
                logger.info(f"Syncthing klasör güncellendi: {folder_id}")
                return

            # HATA-05: Yeni klasör oluştur - devices dict listesi olmalı
            new_folder = {
                "id": folder_id,
                "label": label or folder_id,
                "path": folder_path,
                "type": "sendreceive",
                "devices": [
                    {"deviceID": did, "encryptionPassword": ""} for did in device_ids
                ],
                "rescanIntervalS": 60,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 10,
                "ignorePerms": True,
                "autoNormalize": True,
                "minDiskFreePct": 1,
                "versioning": {"type": "", "params": {}},
                "copiers": 0,
                "pullerMaxPendingKiB": 0,
                "hashers": 0,
                "order": "random",
                "ignoreDelete": False,
                "scanProgressIntervalS": 0,
                "pullerPauseS": 0,
                "maxConflicts": 10,
                "disableSparseFiles": False,
                "disableTempIndexes": False,
                "paused": False,
                "weakHashThresholdPct": 25,
                "markerName": ".stfolder",
                "copyOwnershipFromParent": False,
                "modTimeWindowS": 0,
                "maxConcurrentWrites": 2,
                "disableFsync": False,
                "blockPullOrder": "",
                "copyRangeMethod": "",
                "caseSensitiveFS": False,
                "junctionsAsDirs": False,
                "syncOwnership": False,
                "sendOwnership": False,
                "syncXattrs": False,
                "sendXattrs": False,
                "xattrFilter": {
                    "entries": [],
                    "maxSingleEntrySize": 1000,
                    "maxTotalSize": 10000,
                },
            }

            folders.append(new_folder)

            # HATA-04: PUT payload direkt liste olmalı, dict değil
            response = requests.put(
                f"{self.api_base}/rest/config/folders",
                headers=self._headers,
                json=folders,  # Direkt liste gönder
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"Syncthing klasör eklendi: {folder_id} → {folder_path}")

        except requests.RequestException as e:
            raise ServiceError(f"Syncthing klasör paylaşılamadı: {e}") from e

    def update_folder_path(self, folder_id: str, new_path: str) -> None:
        """Paylaşılan klasörün disk üzerindeki yolunu günceller."""
        try:
            folders = self.get_folders()
            for folder in folders:
                if folder.get("id") == folder_id:
                    folder["path"] = new_path
                    response = requests.put(
                        f"{self.api_base}/rest/config/folders/{folder_id}",
                        headers=self._headers,
                        json=folder,
                        timeout=10,
                    )
                    response.raise_for_status()
                    logger.info(
                        f"Syncthing klasör yolu güncellendi: {folder_id} → {new_path}"
                    )
                    return
            # Klasör henüz yoksa oluştur
            self.share_folder(
                folder_id=folder_id,
                folder_path=new_path,
                device_ids=[],
                label="AHWS Web Site",
            )
        except Exception as e:
            logger.warning(f"Syncthing klasör yolu güncellenemedi: {e}")

    def get_connections(self) -> dict:
        """Uzak cihazların canlı bağlantı durumlarını döndürür (/rest/system/connections)."""
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/system/connections",
                headers=self._headers,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("connections", {}) if isinstance(data, dict) else {}
        except requests.RequestException:
            return {}

    def get_sync_status(self) -> dict:
        """Senkronizasyon durumunu döndürür."""
        try:
            self.sync_credentials_from_config()
            response = requests.get(
                f"{self.api_base}/rest/system/status",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "myID": data.get("myID", ""),
                "uptime": data.get("uptime", 0),
                "goroutines": data.get("goroutines", 0),
                "alloc": data.get("alloc", 0),
                "connectionServiceStatus": data.get("connectionServiceStatus", {}),
            }
        except requests.RequestException as e:
            raise ServiceError(f"Syncthing durum alınamadı: {e}") from e

    # ─── Kaldırma ───────────────────────────────────────────────────
    def restart(self) -> None:
        """Syncthing servisini yeniden başlatır."""
        self.nssm.restart(constants.SERVICE_SYNCTHING)

    def uninstall(self) -> None:
        """Syncthing servisini durdurur ve kaldırır."""
        logger.info("Syncthing servisi kaldırılıyor...")
        self.nssm.remove(constants.SERVICE_SYNCTHING)
        remove_firewall_rule(constants.FIREWALL_RULE_SYNCTHING)
        logger.info("Syncthing servisi kaldırıldı")

    def get_status(self) -> dict:
        """Syncthing servisinin durumunu döndürür."""
        return {
            "name": constants.SERVICE_SYNCTHING,
            "is_installed": self.is_installed(),
            "is_running": self.is_running(),
        }
