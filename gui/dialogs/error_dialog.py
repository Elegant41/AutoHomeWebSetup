"""
Hata mesaj kutusu diyaloğu.

Kullanıcı dostu hata gösterimi sağlar.
"""

import os
import tkinter as tk

from gui import theme
from gui.widgets import PrimaryButton, SecondaryButton, StyledLabel
from utils import constants
from utils.i18n import t


class ErrorDialog(tk.Toplevel):
    """Hata mesajı gösteren modal diyalog."""

    def __init__(self, parent, title: str, message: str, details: str = ""):
        super().__init__(parent)

        self.title(title)
        self.geometry("520x360")
        self.resizable(False, False)
        self.configure(bg=theme.BG_COLOR)
        self.transient(parent)

        try:
            from utils.resource_path import resource_path
            icon_path = resource_path("assets/icon.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass

        try:
            self.grab_set()
        except Exception:
            pass

        # Pencereyi merkeze konumlandır
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 360) // 2
        self.geometry(f"+{x}+{y}")

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=theme.PADDING_LARGE)
        content.pack(fill=tk.BOTH, expand=True)

        # Hata ikonu
        icon_label = StyledLabel(
            content,
            text="✕",
            font=("Segoe UI", 36, "bold"),
            fg=theme.ERROR_COLOR,
            bg=theme.BG_COLOR,
        )
        icon_label.pack(pady=(5, 8))

        # Başlık
        title_label = StyledLabel(
            content,
            text=title,
            font=theme.FONT_LARGE,
            fg=theme.ERROR_COLOR,
            bg=theme.BG_COLOR,
            wraplength=440,
            justify=tk.CENTER,
        )
        title_label.pack(pady=(0, theme.PADDING_SMALL))

        # Mesaj
        message_label = StyledLabel(
            content,
            text=message,
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
            wraplength=440,
            justify=tk.CENTER,
        )
        message_label.pack(pady=(0, theme.PADDING_MEDIUM))

        # Detaylar (opsiyonel)
        if details:
            details_label = StyledLabel(
                content,
                text=details,
                font=theme.FONT_SMALL,
                fg=theme.FG_DISABLED,
                bg=theme.BG_COLOR,
                wraplength=440,
                justify=tk.LEFT,
            )
            details_label.pack(pady=(0, theme.PADDING_MEDIUM))

        # Alt butonlar
        btn_row = tk.Frame(content, bg=theme.BG_COLOR)
        btn_row.pack(side=tk.BOTTOM, pady=(theme.PADDING_SMALL, 0))

        logs_btn = SecondaryButton(
            btn_row,
            text=t("btn_open_logs"),
            command=self._open_logs,
            width=18,
        )
        logs_btn.pack(side=tk.LEFT, padx=(0, theme.PADDING_SMALL))

        close_btn = PrimaryButton(
            btn_row,
            text=t("btn_close"),
            command=self.destroy,
            width=12,
        )
        close_btn.pack(side=tk.LEFT)

    def _open_logs(self) -> None:
        """Log dosyasını veya klasörünü açar."""
        log_file = constants.LOGS_DIR / "ahws.log"
        target = log_file if log_file.exists() else constants.LOGS_DIR
        try:
            if hasattr(os, "startfile"):
                os.startfile(str(target))
        except Exception:
            pass