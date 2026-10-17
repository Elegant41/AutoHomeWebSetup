"""
AutoHomeWebSetup - Tema Sabitleri ve Windows Koyu Başlık Çubuğu Desteği

Modern koyu tema (Catppuccin Mocha esintili) renk paleti, fontlar ve boşluk sabitleri.
"""

import sys

# ─── Renk Paleti (Modern Koyu Tema) ──────────────────────────────────
BG_HEADER = "#141420"          # Üst navigasyon / stepper bar arka planı
BG_COLOR = "#1e1e2e"           # Ana arka plan (koyu mor-lacivert)
BG_SECONDARY = "#262638"       # İkincil arka plan (kartlar)
BG_TERTIARY = "#313244"        # Üçüncül arka plan (input / iç kutular)

CARD_BORDER = "#383a52"        # Kart ince kenarlık rengi
CARD_BORDER_ACTIVE = "#89b4fa" # Seçili / aktif kart kenarlığı

FG_COLOR = "#cdd6f4"           # Ana metin rengi (açık gri-beyaz)
FG_SECONDARY = "#a6adc8"       # İkincil metin rengi
FG_DISABLED = "#6c7086"        # Pasif metin rengi

ACCENT_COLOR = "#89b4fa"       # Vurgu rengi (açık mavi)
ACCENT_HOVER = "#74c7ec"       # Vurgu hover rengi
ACCENT_ACTIVE = "#5e81ac"      # Vurgu aktif rengi

SUCCESS_COLOR = "#a6e3a1"      # Başarı (yeşil)
WARNING_COLOR = "#f9e2af"      # Uyarı (sarı)
ERROR_COLOR = "#f38ba8"        # Hata (kırmızı/mercan)
INFO_COLOR = "#89dceb"         # Bilgi (camgöbeği)

BUTTON_BG = "#3b3d52"          # İkincil buton arka plan
BUTTON_HOVER = "#4e516b"       # İkincil buton hover
BUTTON_ACTIVE = "#313244"      # İkincil buton aktif/pressed

BUTTON_PRIMARY_BG = "#2563eb"  # Birincil buton (canlı modern mavi)
BUTTON_PRIMARY_HOVER = "#3b82f6"
BUTTON_PRIMARY_ACTIVE = "#1d4ed8"

BUTTON_DANGER_BG = "#be123c"   # Tehlikeli işlem butonu (kırmızı)
BUTTON_DANGER_HOVER = "#e11d48"
BUTTON_DANGER_ACTIVE = "#9f1239"

BUTTON_TEXT = "#ffffff"        # Buton metni
BUTTON_DISABLED_BG = "#313244" # Pasif buton arkaplanı
BUTTON_DISABLED_TEXT = "#6c7086"

PROGRESS_BG = "#313244"        # İlerleme çubuğu arka plan
PROGRESS_FILL = "#3b82f6"      # İlerleme çubuğu dolu kısmı

LOG_BG = "#11111b"             # Log alanı arka planı
LOG_FG = "#cdd6f4"             # Log alanı metni

ENTRY_BG = "#181825"           # Entry arka planı (kart içinde derinlik hissi verir)
ENTRY_FG = "#cdd6f4"           # Entry metni
ENTRY_BORDER = "#45475a"       # Entry kenarlık

# ─── Fontlar ─────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_SIZE_SMALL = 9
FONT_SIZE_NORMAL = 10
FONT_SIZE_MEDIUM = 12
FONT_SIZE_LARGE = 15
FONT_SIZE_TITLE = 22

FONT_SMALL = (FONT_FAMILY, FONT_SIZE_SMALL)
FONT_SMALL_BOLD = (FONT_FAMILY, FONT_SIZE_SMALL, "bold")
FONT_NORMAL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_NORMAL_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_MEDIUM = (FONT_FAMILY, FONT_SIZE_MEDIUM, "bold")
FONT_LARGE = (FONT_FAMILY, FONT_SIZE_LARGE, "bold")
FONT_TITLE = (FONT_FAMILY, FONT_SIZE_TITLE, "bold")

FONT_MONO_NORMAL = (FONT_FAMILY_MONO, FONT_SIZE_NORMAL)
FONT_MONO_SMALL = (FONT_FAMILY_MONO, FONT_SIZE_SMALL)

# ─── Boyutlar & Boşluklar ────────────────────────────────────────────
PADDING_XS = 4
PADDING_SMALL = 8
PADDING_MEDIUM = 16
PADDING_LARGE = 24
PADDING_XL = 32

BORDER_RADIUS = 8
BORDER_WIDTH = 1
BUTTON_HEIGHT = 36
BUTTON_WIDTH = 12
ENTRY_WIDTH = 40
CHECKBUTTON_SELECTOR_COLOR = "#89b4fa"

# ─── Widget Stil Sabitleri ───────────────────────────────────────────
PROGRESSBAR_HEIGHT = 14
LOG_WIDTH = 80
LOG_HEIGHT = 11
LISTBOX_BG = "#11111b"
LISTBOX_FG = "#cdd6f4"
LISTBOX_SELECT_BG = "#5e81ac"
LISTBOX_SELECT_FG = "#ffffff"


def apply_dark_titlebar(window) -> None:
    """Windows 10/11 pencerelerinde başlık çubuğunu (title bar) koyu temaya geçirir."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            hwnd = window.winfo_id()
        value = ctypes.c_int(1)
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (Windows 10 20H1+ & Windows 11), 19 (eski Win10)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 19, ctypes.byref(value), ctypes.sizeof(value)
        )
    except Exception:
        pass