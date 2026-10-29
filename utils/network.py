"""
Ağ yardımcıları.

Port kontrolü, bağlantı testi ve ağ durumu tespiti.
"""

import socket
import urllib.request
import concurrent.futures

from utils.logger import get_logger

logger = get_logger(__name__)


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Belirtilen portun kullanılabilir olup olmadığını kontrol eder.

    Args:
        port: Kontrol edilecek port numarası
        host: Kontrol edilecek host (varsayılan: localhost)

    Returns:
        True: Port kullanılabilir
        False: Port zaten kullanımda
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False
    except Exception as e:
        logger.warning(f"Port kontrolü sırasında hata: {e}")
        return False


def is_port_in_use_by_caddy(port: int) -> bool:
    """
    Belirtilen portun mevcut AHWS Caddy servisi veya caddy.exe tarafından
    kullanılıp kullanılmadığını kontrol eder.

    Args:
        port: Kontrol edilecek port numarası

    Returns:
        bool: Port Caddy tarafından kullanılıyorsa True
    """
    try:
        from utils.platform_utils import run_command
        from utils import constants

        # 1. Caddyfile içinde bu port tanımlıysa ve servis çalışıyorsa
        if constants.CADDYFILE_PATH.exists():
            try:
                content = constants.CADDYFILE_PATH.read_text(encoding="utf-8")
                if f":{port} " in content or f":{port}\n" in content or f":{port}{{" in content:
                    from services.windows_service import SCService
                    if SCService.is_running(constants.SERVICE_CADDY):
                        return True
            except Exception:
                pass

        # 2. Portu dinleyen süreç caddy.exe mi kontrol et
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue | "
            f"ForEach-Object {{ (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName }}",
        ]
        res = run_command(cmd, timeout=5)
        if "caddy" in res.stdout.lower():
            return True
    except Exception as e:
        logger.warning(f"Caddy port kontrol hatası: {e}")
    return False


def check_local_http_health(port: int = 80, timeout: int = 3) -> bool:
    """
    Yerel Caddy sunucusunun sağlık durumunu kontrol eder (/ahws-health veya /).
    """
    def check_path(path: str) -> bool:
        try:
            url = f"http://127.0.0.1:{port}{path}"
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                if 200 <= resp.status < 400:
                    return True
        except Exception:
            pass
        return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(check_path, path) for path in ("/ahws-health", "/")]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                return True
    return False


def get_local_ip() -> str:
    """
    Makinenin yerel IP adresini döndürür.

    Returns:
        str: Yerel IP adresi (bulunamazsa "127.0.0.1")
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Hedefe bağlanmaya gerek yok, sadece route'u belirler
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        logger.warning(f"Yerel IP alınamadı: {e}")
        return "127.0.0.1"


def check_internet_connection(timeout: int = 5) -> bool:
    """
    İnternet bağlantısının olup olmadığını kontrol eder.

    Args:
        timeout: Zaman aşımı saniye

    Returns:
        True: İnternet bağlantısı var
        False: İnternet bağlantısı yok
    """
    try:
        urllib.request.urlopen("https://www.cloudflare.com", timeout=timeout)
        return True
    except Exception:
        return False


def check_tcp_connection(host: str, port: int, timeout: int = 5) -> bool:
    """
    Belirtilen host:port'a TCP bağlantısı kurulabilir mi kontrol eder.

    Args:
        host: Hedef host
        port: Hedef port
        timeout: Zaman aşımı saniye

    Returns:
        True: Bağlantı kurulabildi
        False: Bağlantı kurulamadı
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def find_available_port(preferred: int, max_attempts: int = 20) -> int:
    """
    Tercih edilen porttan başlayarak kullanılabilir bir port bulur.

    Args:
        preferred: Tercih edilen port numarası
        max_attempts: Maksimum deneme sayısı

    Returns:
        int: Kullanılabilir port numarası (bulunamazsa -1)
    """
    for port in range(preferred, preferred + max_attempts):
        if is_port_available(port):
            return port
    return -1