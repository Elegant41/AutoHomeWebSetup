"""
AutoHomeWebSetup - Sabitler
Tüm uygulama genelinde kullanılan sabit değerler.
"""

import string
from pathlib import Path

# ─── Uygulama Bilgileri ───────────────────────────────────────────────
APP_NAME = "AHWS"
APP_DISPLAY_NAME = "AHWS - HA Kurulum Sihirbazı"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Windows kullanıcıları için statik web siteleri "
    "otomatik failover ağı kurulum sihirbazı"
)

# ─── Dizin Yolları ────────────────────────────────────────────────────
PROGRAMDATA_DIR = Path(r"C:\ProgramData\AHWS")
INSTALL_DIR = PROGRAMDATA_DIR
BIN_DIR = INSTALL_DIR / "bin"
CONFIG_DIR = INSTALL_DIR / "config"
LOGS_DIR = INSTALL_DIR / "logs"
SITE_DIR = INSTALL_DIR / "site"
SYNCTHING_HOME_DIR = CONFIG_DIR / "syncthing"

# ─── Varsayılan Portlar ───────────────────────────────────────────────
CADDY_DEFAULT_PORT = 80
SYNCTHING_GUI_PORT = 8384
SYNCTHING_GUI_PORT_ALT = 8385  # Çakışma durumunda alternatif
SYNCTHING_API_PORT = 8384

# ─── Servis İsimleri ──────────────────────────────────────────────────
SERVICE_CADDY = "AHWS-Caddy"
SERVICE_CLOUDFLARED = "Cloudflared"
SERVICE_SYNCTHING = "AHWS-Syncthing"

# ─── Güvenlik Duvarı Kural İsimleri ───────────────────────────────────
FIREWALL_RULE_CADDY = "AHWS-Caddy-Web"
FIREWALL_RULE_SYNCTHING = "AHWS-Syncthing-Sync"

# ─── Küme Katılım Kodu (Join Key) Ön Eki ──────────────────────────────
JOIN_KEY_PREFIX = "AHWS1-"

# ─── Binary Dosya İsimleri ────────────────────────────────────────────
CADDY_EXE = "caddy.exe"
CLOUDFLARED_EXE = "cloudflared.exe"
SYNCTHING_EXE = "syncthing.exe"
NSSM_EXE = "nssm.exe"

# ─── GitHub Release URL'leri ──────────────────────────────────────────
# Not: Versiyonlar sabit değil, güncel sürüm için API çağrısı yapılacak.
# Bu URL'ler indirme template'leri olarak kullanılacak.
CADDY_RELEASE_API = "https://api.github.com/repos/caddyserver/caddy/releases/latest"
CADDY_DOWNLOAD_PATTERN = (
    "https://github.com/caddyserver/caddy/releases/download/"
    "v{version}/caddy_{version}_windows_amd64.zip"
)

CLOUDFLARED_RELEASE_API = (
    "https://api.github.com/repos/cloudflare/cloudflared/releases/latest"
)
CLOUDFLARED_DOWNLOAD_PATTERN = (
    "https://github.com/cloudflare/cloudflared/releases/download/"
    "{version}/cloudflared-windows-amd64.exe"
)

SYNCTHING_RELEASE_API = (
    "https://api.github.com/repos/syncthing/syncthing/releases/latest"
)
SYNCTHING_DOWNLOAD_PATTERN = (
    "https://github.com/syncthing/syncthing/releases/download/"
    "v{version}/syncthing-windows-amd64-v{version}.zip"
)

# ─── Loglama ──────────────────────────────────────────────────────────
LOG_FILE = LOGS_DIR / "installer.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "DEBUG"
GUI_LOG_MAX_LINES = 500

# ─── Syncthing API ────────────────────────────────────────────────────
SYNCTHING_API_KEY_LENGTH = 32
# HATA-12: API anahtarı için büyük/küçük harf + rakamlar (zayıf entropi düzeltildi)
SYNCTHING_API_KEY_CHARS = string.ascii_letters + string.digits
SYNCTHING_API_TIMEOUT = 30  # API'ye bağlanmak için maksimum bekleme süresi (saniye)
SYNCTHING_API_RETRY_INTERVAL = 0.5  # Her polling arası bekleme (saniye)

# ─── Caddyfile ────────────────────────────────────────────────────────
CADDYFILE_PATH = CONFIG_DIR / "Caddyfile"

# ─── İndirme Ayarları ─────────────────────────────────────────────────
DOWNLOAD_TIMEOUT = 120  # Tek bir indirme için maksimum süre (saniye)
DOWNLOAD_RETRY_COUNT = 3
DOWNLOAD_RETRY_DELAY = 3  # Exponential backoff başlangıç beklemesi (saniye)
DOWNLOAD_CHUNK_SIZE = 8192  # Bayt cinsinden chunk boyutu

# ─── GUI Ayarları ─────────────────────────────────────────────────────
WINDOW_TITLE = APP_DISPLAY_NAME
WINDOW_WIDTH = 860
WINDOW_HEIGHT = 720
WINDOW_MIN_WIDTH = 780
WINDOW_MIN_HEIGHT = 650
PAGE_PADDING = 20

# ─── Device ID Regex (Syncthing) ──────────────────────────────────────
# Format: AAAA-BBBBBBB-CCCCCC-DDDDDDD-EEEEEEE-FFFFFF-GGGGGGG-HHHHHHH
DEVICE_ID_REGEX = r"^[A-Z0-9]{7}(-[A-Z0-9]{7}){7}$"

# ─── Cloudflare Tunnel Token Regex ────────────────────────────────────
# Token formatı: eyJ... (Base64 veya JWT formatında)
CLOUDFLARE_TOKEN_REGEX = r"^eyJ[A-Za-z0-9\-_=.+/]+$"


def clean_cloudflare_token(raw: str) -> str:
    """Yapıştırılan metinden (komut, tırnak, boşluk vb. dahil) temiz token'ı ayıklar."""
    import re
    if not raw:
        return ""
    stripped = raw.strip().strip('"\'')
    match = re.search(r"eyJ[A-Za-z0-9\-_=.+/]+", stripped)
    if match:
        return match.group(0)
    return stripped
