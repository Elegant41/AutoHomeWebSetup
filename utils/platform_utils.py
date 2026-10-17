"""
Windows platform yardımcıları.

UAC yönetici yetkisi kontrolü, elevation ve Windows'a özgü
dizin/yol işlemleri.
"""

import ctypes
import os
import subprocess
import sys
from pathlib import Path

from utils import constants
from utils.resource_path import is_frozen


def is_valid_binary(path: Path | str, min_size: int = 1) -> bool:
    """
    Dosyanın var olduğunu ve 0 bayttan büyük olduğunu kontrol eder.

    Args:
        path: Kontrol edilecek dosya yolu
        min_size: Minimum geçerli dosya boyutu (bayt cinsinden, varsayılan: 1 bayt)

    Returns:
        bool: Geçerli ve boş olmayan bir çalıştırılabilir dosya ise True
    """
    try:
        p = Path(path)
        return p.exists() and p.is_file() and p.stat().st_size >= min_size
    except Exception:
        return False


def is_admin() -> bool:
    """
    Uygulamanın yönetici yetkileriyle çalışıp çalışmadığını kontrol eder.

    Returns:
        True: Yönetici yetkisi aktif
        False: Yönetici yetkisi yok (veya Windows dışında çalışıyor)
    """
    # Windows dışındaki platformlarda kontrol yapma
    if os.name != "nt":
        return True

    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate() -> None:
    """
    Uygulamayı yönetici olarak yeniden başlatır.

    ShellExecuteW ile 'runas' (UAC promptu) kullanarak mevcut süreci
    yönetici yetkisiyle yeniden başlatır. Çağrıldığı süreç sonlandırılır.
    """
    if os.name != "nt":
        return

    if is_frozen():
        # PyInstaller tek dosya (onefile) modunda
        executable = sys.executable
        params = " ".join(sys.argv[1:])
    else:
        # Geliştirme modunda: python main.py [args]
        executable = sys.executable
        script_path = Path(sys.argv[0]).resolve()
        params = f'"{script_path}" ' + " ".join(sys.argv[1:])

    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            params,
            None,
            1  # SW_SHOWNORMAL
        )
    except Exception as e:
        # Kullanıcı UAC promptunu reddederse veya hata olursa
        raise SystemExit(f"Yönetici yetkisi gerekli. Hata: {e}")

    sys.exit(0)


def ensure_admin() -> None:
    """
    Uygulamanın başında yönetici yetkisi yoksa elevation tetikler.
    """
    if not is_admin():
        elevate()


def get_install_dir() -> Path:
    """
    Kurulum dizinini döndürür.

    Returns:
        C:\\ProgramData\\AHWS
    """
    return constants.INSTALL_DIR


def get_programdata_dir() -> Path:
    """ProgramData dizinini döndürür (env var ile genişletilir)."""
    base = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    return Path(base) / constants.APP_NAME


def create_app_directories() -> None:
    """
    Uygulamaya ait tüm dizinleri oluşturur.

    Oluşturulan dizinler:
        - C:\\ProgramData\\AHWS
        - C:\\ProgramData\\AHWS\\bin
        - C:\\ProgramData\\AHWS\\config
        - C:\\ProgramData\\AHWS\\config\\syncthing
        - C:\\ProgramData\\AHWS\\logs
        - C:\\ProgramData\\AHWS\\site
    """
    dirs = [
        constants.INSTALL_DIR,
        constants.BIN_DIR,
        constants.CONFIG_DIR,
        constants.SYNCTHING_HOME_DIR,
        constants.LOGS_DIR,
        constants.SITE_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def add_firewall_rule(rule_name: str, exe_path: str) -> bool:
    """
    Windows Güvenlik Duvarı'na belirtilen uygulama için gelen/giden izin kuralı ekler.

    Args:
        rule_name: Kural adı
        exe_path: İzin verilecek .exe dosyasının tam yolu

    Returns:
        bool: Başarılı ise True
    """
    if os.name != "nt":
        return True
    try:
        # Önce aynı isimde eski kural varsa sil
        run_command([
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name={rule_name}",
        ])
        # Gelen (Inbound) bağlantılara izin ver
        res_in = run_command([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}",
            "dir=in",
            "action=allow",
            f"program={exe_path}",
            "enable=yes",
            "profile=any",
        ])
        # Giden (Outbound) bağlantılara izin ver
        res_out = run_command([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}",
            "dir=out",
            "action=allow",
            f"program={exe_path}",
            "enable=yes",
            "profile=any",
        ])
        return res_in.returncode == 0 and res_out.returncode == 0
    except Exception:
        return False


def remove_firewall_rule(rule_name: str) -> bool:
    """
    Windows Güvenlik Duvarı'ndan belirtilen kuralı kaldırır.
    """
    if os.name != "nt":
        return True
    try:
        res = run_command([
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name={rule_name}",
        ])
        return res.returncode == 0
    except Exception:
        return False


def disable_sleep_on_ac() -> bool:
    """
    Bilgisayar prize takılıyken (AC) uyku ve hazırda bekletme moduna geçmesini engeller.
    Sunucunun 7/24 erişilebilir kalması için kullanılır.
    """
    if os.name != "nt":
        return True
    try:
        res1 = run_command(["powercfg", "/change", "standby-timeout-ac", "0"])
        res2 = run_command(["powercfg", "/change", "hibernate-timeout-ac", "0"])
        return res1.returncode == 0 and res2.returncode == 0
    except Exception:
        return False


def _decode_output(data: bytes | str | None) -> str:
    """
    Subprocess çıktısını güvenli bir şekilde metne dönüştürür.
    UTF-8, UTF-16, CP1254 (Türkçe Windows) dener ve null baytları temizler.
    """
    if data is None:
        return ""
    if isinstance(data, str):
        return data.replace("\x00", "")
    if not data:
        return ""
    for enc in ("utf-8", "utf-16", "cp1254", "cp1252", "latin-1"):
        try:
            decoded = data.decode(enc)
            return decoded.replace("\x00", "")
        except (UnicodeDecodeError, ValueError):
            continue
    return data.decode("utf-8", errors="replace").replace("\x00", "")


def run_command(
    cmd: list[str],
    cwd: str | None = None,
    timeout: int | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Windows'ta terminal penceresi belirmeden komut çalıştırır.

    Tüm subprocess çağrılarında terminal penceresinin belirmemesi için
    CREATE_NO_WINDOW flag'i eklenir.

    Args:
        cmd: Komut ve argümanlar listesi
        cwd: Çalışma dizini (opsiyonel)
        timeout: Zaman aşımı saniye (opsiyonel)
        capture_output: Çıktıyı yakala (True ise terminalde görünmez)

    Returns:
        subprocess.CompletedProcess nesnesi

    Raises:
        subprocess.CalledProcessError: Komut başarısız olursa (check=True)
        TimeoutExpired: Zaman aşımı olursa
    """
    creationflags = 0x08000000  # CREATE_NO_WINDOW

    kwargs = {
        "cwd": cwd,
        "capture_output": capture_output,
        "creationflags": creationflags,
        "timeout": timeout,
    }

    result = subprocess.run(cmd, **kwargs)

    stdout_str = _decode_output(result.stdout) if capture_output else ""
    stderr_str = _decode_output(result.stderr) if capture_output else ""

    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout=stdout_str,
        stderr=stderr_str,
    )