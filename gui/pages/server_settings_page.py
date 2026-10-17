"""
Sunucu Ayarları sayfası.

Web sitesi klasörü seçimi, Cloudflare Tunnel token girişi ve
port ayarı içerir.
"""

import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from gui import theme
from gui.base_page import BasePage
from gui.widgets import (
    CardFrame,
    HeaderFrame,
    PrimaryButton,
    SecondaryButton,
    StyledEntry,
    StyledLabel,
)
from utils import constants
from utils.logger import get_logger
from utils.network import is_port_available, is_port_in_use_by_caddy
from utils.i18n import t

logger = get_logger(__name__)


class ServerSettingsPage(BasePage):
    """2. Adım: Sunucu Ayarları (Web sitesi klasörü + Tunnel token + Port)."""

    PAGE_NAME = "server_settings"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # ─── Başlık ─────────────────────────────────────────────────
        header = HeaderFrame(
            self,
            title=t("server_title"),
            subtitle=t("server_subtitle"),
        )
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(theme.PADDING_LARGE, theme.PADDING_MEDIUM))

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=theme.PADDING_MEDIUM)

        # ─── Web Sitesi Klasörü ─────────────────────────────────────
        folder_card = CardFrame(content)
        folder_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        folder_title = StyledLabel(
            folder_card,
            text=t("server_folder_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        folder_title.pack(anchor=tk.W, pady=(0, 2))

        self.folder_desc = StyledLabel(
            folder_card,
            text=t("server_folder_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
        )
        self.folder_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        folder_row = tk.Frame(folder_card, bg=theme.BG_SECONDARY)
        folder_row.pack(fill=tk.X)

        self.folder_var = tk.StringVar()
        self.folder_entry = StyledEntry(
            folder_row,
            textvariable=self.folder_var,
            width=50,
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, theme.PADDING_SMALL))

        browse_btn = SecondaryButton(
            folder_row,
            text=t("btn_browse"),
            command=self._browse_folder,
            width=14,
        )
        browse_btn.pack(side=tk.RIGHT)

        # ─── Cloudflare Tunnel Token ─────────────────────────────────
        token_card = CardFrame(content)
        token_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        token_title = StyledLabel(
            token_card,
            text=t("server_token_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        token_title.pack(anchor=tk.W, pady=(0, 2))

        token_desc = StyledLabel(
            token_card,
            text=t("server_token_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
        )
        token_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.token_var = tk.StringVar()
        self.token_entry = StyledEntry(
            token_card,
            textvariable=self.token_var,
            width=60,
            show="•",
        )
        self.token_entry.pack(fill=tk.X)

        # ─── Public Domain (Opsiyonel) ──────────────────────────────
        domain_card = CardFrame(content)
        domain_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        domain_title = StyledLabel(
            domain_card,
            text=t("server_domain_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        domain_title.pack(anchor=tk.W, pady=(0, 2))

        domain_desc = StyledLabel(
            domain_card,
            text=t("server_domain_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
        )
        domain_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.domain_var = tk.StringVar()
        self.domain_entry = StyledEntry(
            domain_card,
            textvariable=self.domain_var,
            width=60,
        )
        self.domain_entry.pack(fill=tk.X)

        # ─── Port ve Güç Ayarları ───────────────────────────────────
        port_card = CardFrame(content)
        port_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        port_title = StyledLabel(
            port_card,
            text=t("server_port_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        port_title.pack(anchor=tk.W, pady=(0, 2))

        port_desc = StyledLabel(
            port_card,
            text=t("server_port_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
        )
        port_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        port_row = tk.Frame(port_card, bg=theme.BG_SECONDARY)
        port_row.pack(fill=tk.X)

        self.port_var = tk.StringVar(value=str(constants.CADDY_DEFAULT_PORT))
        self.port_spinbox = tk.Spinbox(
            port_row,
            from_=1,
            to=65535,
            textvariable=self.port_var,
            width=10,
            font=theme.FONT_NORMAL,
            bg=theme.ENTRY_BG,
            fg=theme.ENTRY_FG,
            insertbackground=theme.FG_COLOR,
            relief=tk.FLAT,
            highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.ENTRY_BORDER,
            highlightcolor=theme.ACCENT_COLOR,
            buttonbackground=theme.BUTTON_BG,
        )
        self.port_spinbox.pack(side=tk.LEFT)

        self.port_status_label = StyledLabel(
            port_row,
            text="",
            font=theme.FONT_SMALL,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.port_status_label.pack(side=tk.LEFT, padx=(theme.PADDING_MEDIUM, 0))

        self.prevent_sleep_var = tk.BooleanVar(value=True)
        self.prevent_sleep_cb = tk.Checkbutton(
            port_card,
            text=t("server_prevent_sleep"),
            variable=self.prevent_sleep_var,
            font=theme.FONT_SMALL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            selectcolor=theme.BG_TERTIARY,
            activebackground=theme.BG_SECONDARY,
            activeforeground=theme.FG_COLOR,
            highlightthickness=0,
        )
        self.prevent_sleep_cb.pack(anchor=tk.W, pady=(theme.PADDING_SMALL, 0))

        # Port değişimini dinle
        self.port_var.trace_add("write", self._on_port_change)

        # ─── Alt Butonlar ───────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=theme.PADDING_SMALL)

        back_btn = SecondaryButton(
            footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=12,
        )
        back_btn.pack(side=tk.LEFT)

        self.next_btn = PrimaryButton(
            footer,
            text=t("btn_start_install"),
            command=self.next_page,
            width=16,
        )
        self.next_btn.pack(side=tk.RIGHT)

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def _get_current_role(self) -> str:
        """Seçili düğüm rolünü döndürür ('primary' veya 'secondary')."""
        if self.controller:
            sync_data = self.controller.get_saved_page_data("sync_settings")
            if sync_data and sync_data.get("node_role"):
                return sync_data["node_role"]
        return "primary"

    def _browse_folder(self) -> None:
        """Klasör seçici diyaloğunu açar."""
        initial_dir = self.folder_var.get() or str(Path.home())
        selected = filedialog.askdirectory(
            parent=self,
            title=t("btn_browse"),
            initialdir=initial_dir,
        )
        if selected:
            self.folder_var.set(selected)
            self._update_port_status()

    def _on_port_change(self, *_args) -> None:
        """Port değeri değiştiğinde durum günceller."""
        self._update_port_status()

    def _update_port_status(self) -> None:
        """Port durumunu günceller."""
        try:
            port = int(self.port_var.get() or "0")
            if 1 <= port <= 65535:
                if is_port_available(port):
                    self.port_status_label.config(text=t("server_port_ok"), fg=theme.SUCCESS_COLOR)
                elif is_port_in_use_by_caddy(port):
                    self.port_status_label.config(text=t("server_port_caddy_reinstall"), fg=theme.SUCCESS_COLOR)
                else:
                    self.port_status_label.config(text=t("server_port_in_use"), fg=theme.ERROR_COLOR)
            else:
                self.port_status_label.config(text=t("server_port_invalid"), fg=theme.ERROR_COLOR)
        except ValueError:
            self.port_status_label.config(text=t("server_port_invalid"), fg=theme.ERROR_COLOR)

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde verileri ve rol bazlı açıklamaları güncelle."""
        role = self._get_current_role()
        if role == "secondary":
            self.folder_desc.config(text=t("server_folder_secondary_desc"))
        else:
            self.folder_desc.config(text=t("server_folder_desc"))

        # Önce kayıtlı verileri geri yükle
        if self.controller:
            saved = self.controller.get_saved_page_data(self.PAGE_NAME)
            if saved:
                if saved.get("site_root_path"):
                    self.folder_var.set(saved["site_root_path"])
                if saved.get("cloudflare_token"):
                    self.token_var.set(saved["cloudflare_token"])
                if saved.get("public_domain") is not None:
                    self.domain_var.set(saved["public_domain"])
                if saved.get("caddy_port"):
                    self.port_var.set(str(saved["caddy_port"]))
                if "prevent_sleep" in saved:
                    self.prevent_sleep_var.set(bool(saved["prevent_sleep"]))

        if role == "secondary" and not self.folder_var.get().strip():
            self.folder_var.set(str(constants.SITE_DIR))

        self._update_port_status()

    def validate(self) -> tuple[bool, str]:
        """Sayfa geçiş validasyonu."""
        role = self._get_current_role()
        folder_path = self.folder_var.get().strip()

        if role == "secondary" and not folder_path:
            folder_path = str(constants.SITE_DIR)
            self.folder_var.set(folder_path)

        if not folder_path:
            return False, t("err_no_folder")

        if role == "secondary":
            # Yedek düğümde klasör yoksa otomatik oluştur, index.html şartı arama!
            try:
                Path(folder_path).mkdir(parents=True, exist_ok=True)
            except Exception:
                return False, t("err_folder_not_found", folder=folder_path)
            if not os.path.isdir(folder_path):
                return False, t("err_folder_not_found", folder=folder_path)
        else:
            # Merkez düğümde klasör ve index.html mevcut olmalı
            if not os.path.isdir(folder_path):
                return False, t("err_folder_not_found", folder=folder_path)

            index_path = Path(folder_path) / "index.html"
            if not index_path.is_file():
                return False, t("err_no_index", index_path=index_path)

        # Token kontrolü
        token = self.token_var.get().strip()
        if not token:
            return False, t("err_no_token")
        if not re.match(constants.CLOUDFLARE_TOKEN_REGEX, token):
            return False, t("err_invalid_token")

        # Port kontrolü
        try:
            port = int(self.port_var.get() or "0")
            if not (1 <= port <= 65535):
                return False, t("err_port_range")
            if not is_port_available(port) and not is_port_in_use_by_caddy(port):
                return False, t("err_port_in_use_msg", port=port)
        except ValueError:
            return False, t("server_port_invalid")

        return True, ""

    def get_data(self) -> dict:
        """Sayfa verilerini döndürür."""
        return {
            "site_root_path": self.folder_var.get().strip(),
            "cloudflare_token": self.token_var.get().strip(),
            "public_domain": self.domain_var.get().strip(),
            "caddy_port": int(self.port_var.get() or constants.CADDY_DEFAULT_PORT),
            "prevent_sleep": bool(self.prevent_sleep_var.get()),
        }