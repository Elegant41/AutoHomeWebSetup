"""
PyInstaller uyumlu kaynak yolu çözücü.

PyInstaller --onefile modunda, exe içeriği geçici bir klasöre açılır ve
bu klasör `sys._MEIPASS` değişkeniyle erişilebilir. Kaynak dosyalara
(simgeler, NSSM binary'si vb.) hem geliştirme hem de paketlenmiş
ortamda doğru şekilde erişmek için bu yardımcı fonksiyon kullanılır.
"""

import sys
from pathlib import Path

# type: ignore[attr-defined]
_MEIPASS = getattr(sys, "_MEIPASS", None)


def resource_path(relative_path: str) -> Path:
    """
    Kaynak dosyaların mutlak yolunu döndürür.

    Geliştirme ortamında: Proje kök dizinindeki dosyaları gösterir.
    Paketlenmiş exe'de: sys._MEIPASS altındaki geçici dizini gösterir.

    Args:
        relative_path: Kaynak dosyanın proje köküne göre yolu (örn: "assets/icon.ico")

    Returns:
        Kaynak dosyanın mutlak yolu (Path nesnesi)
    """
    if _MEIPASS:
        return Path(_MEIPASS) / relative_path
    return Path(__file__).resolve().parent.parent / relative_path


def is_frozen() -> bool:
    """Uygulamanın PyInstaller ile paketlenip paketlenmediğini döndürür."""
    return _MEIPASS is not None