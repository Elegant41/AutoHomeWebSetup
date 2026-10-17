"""
Hata mesaj kutusu diyaloğu.

Kullanıcı dostu hata gösterimi sağlar.
"""

import os
import tkinter as tk

from gui import theme
from gui.widgets import CardFrame, PrimaryButton, SecondaryButton, StyledLabel
from utils import constants
from utils.i18n import t


class ErrorDialog(tk.Toplevel):
    """Hata mesajı gösteren modal diyalog."""

    def __init__(self, parent, title: str, message: str, details: str = ""):
        super().__init__(parent)

        self.title(title)
        self.geometry("540x360")
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
        theme.apply_dark_titlebar(self)

        try:
            self.grab_set()
        except Exception:
            pass

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 540) // 2
        y = (self.winfo_screenheight() - 360) // 2
        self.geometry(f"+{x}+{y}")

        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=theme.PADDING_LARGE)
        content.pack(fill=tk.BOTH, expand=True)

        card = CardFrame(content, border_color=theme.ERROR_COLOR, padx=20, pady=16)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        icon_label = StyledLabel(
            card,
            text="✕",
            font=("Segoe UI", 30, "bold"),
            fg=theme.ERROR_COLOR,
            bg=theme.BG_SECONDARY,
        )
        icon_label.pack(pady=(2, 4))

        title_label = StyledLabel(
            card,
            text=title,
            font=theme.FONT_LARGE,
            fg=theme.ERROR_COLOR,
            bg=theme.BG_SECONDARY,
            wraplength=450,
            justify=tk.CENTER,
        )
        title_label.pack(pady=(0, 6))

        message_label = StyledLabel(
            card,
            text=message,
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            wraplength=450,
            justify=tk.CENTER,
        )
        message_label.pack(pady=(0, 6))

        if details:
            details_label = StyledLabel(
                card,
                text=details,
                font=theme.FONT_SMALL,
                fg=theme.FG_DISABLED,
                bg=theme.BG_SECONDARY,
                wraplength=450,
                justify=tk.LEFT,
            )
            details_label.pack(pady=(0, 4))

        btn_row = tk.Frame(content, bg=theme.BG_COLOR)
        btn_row.pack(side=tk.BOTTOM)

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
            width=14,
        )
        close_btn.pack(side=tk.LEFT)

    def _open_logs(self) -> None:
        """Log dosyasını veya klasörünü açar."""
        log_file = constants.LOG_FILE
        target = log_file if log_file.exists() else constants.LOGS_DIR
        try:
            if hasattr(os, "startfile"):
                os.startfile(str(target))
        except Exception:
            pass