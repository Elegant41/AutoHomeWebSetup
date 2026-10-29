"""
Sunucu Ayarları sayfası.

Web sitesi klasörü seçimi (canlı index.html doğrulamalı),
Cloudflare Tunnel token girişi (Yapıştır + Göster/Gizle destekli),
Public Domain ve Port/Güç ayarlarını içerir.
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
from utils.i18n import t
from utils.logger import get_logger
from utils.network import is_port_available, is_port_in_use_by_caddy

logger = get_logger(__name__)


class ServerSettingsPage(BasePage):
    """3. Adım: Sunucu Ayarları (Web sitesi klasörü + Tunnel token + Domain & Port)."""

    PAGE_NAME = "server_settings"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._token_visible = False

        # ─── Başlık ─────────────────────────────────────────────────
        header = HeaderFrame(
            self,
            title=t("server_title"),
            subtitle=t("server_subtitle"),
        )
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(10, 6))

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=(0, 6))

        # ─── 1. Web Sitesi Klasörü ──────────────────────────────────
        folder_card = CardFrame(content, padx=16, pady=8)
        folder_card.pack(fill=tk.X, pady=(0, 6))

        folder_header = tk.Frame(folder_card, bg=theme.BG_SECONDARY)
        folder_header.pack(fill=tk.X)

        folder_title = StyledLabel(
            folder_header,
            text=t("server_folder_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        folder_title.pack(side=tk.LEFT)

        self.folder_status_label = StyledLabel(
            folder_header,
            text="",
            font=theme.FONT_SMALL_BOLD,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.folder_status_label.pack(side=tk.RIGHT)

        self.folder_desc = StyledLabel(
            folder_card,
            text=t("server_folder_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        self.folder_desc.pack(anchor=tk.W, pady=(2, 6))

        folder_row = tk.Frame(folder_card, bg=theme.BG_SECONDARY)
        folder_row.pack(fill=tk.X)

        browse_btn = SecondaryButton(
            folder_row,
            text=t("btn_browse"),
            command=self._browse_folder,
            width=12,
        )
        browse_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.folder_var = tk.StringVar()
        self.folder_entry = StyledEntry(
            folder_row,
            textvariable=self.folder_var,
            width=50,
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.folder_var.trace_add("write", self._on_folder_change)

        # ─── 2. Cloudflare Tunnel Token ─────────────────────────────
        token_card = CardFrame(content, padx=16, pady=10)
        token_card.pack(fill=tk.X, pady=(0, 8))

        token_title = StyledLabel(
            token_card,
            text=t("server_token_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        token_title.pack(anchor=tk.W)

        token_desc = StyledLabel(
            token_card,
            text=t("server_token_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        token_desc.pack(anchor=tk.W, pady=(2, 6))

        token_row = tk.Frame(token_card, bg=theme.BG_SECONDARY)
        token_row.pack(fill=tk.X)

        self.toggle_token_btn = SecondaryButton(
            token_row,
            text=t("btn_show"),
            command=self._toggle_token_visibility,
            width=8,
        )
        self.toggle_token_btn.pack(side=tk.RIGHT, padx=(6, 0))

        paste_token_btn = SecondaryButton(
            token_row,
            text=t("btn_paste"),
            command=self._paste_token,
            width=10,
        )
        paste_token_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.token_var = tk.StringVar()
        self.token_entry = StyledEntry(
            token_row,
            textvariable=self.token_var,
            font=theme.FONT_MONO_SMALL,
            width=50,
            show="•",
        )
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        # ─── 3. Public Domain (Opsiyonel) ───────────────────────────
        domain_card = CardFrame(content, padx=16, pady=10)
        domain_card.pack(fill=tk.X, pady=(0, 8))

        domain_title = StyledLabel(
            domain_card,
            text=t("server_domain_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        domain_title.pack(anchor=tk.W)

        domain_desc = StyledLabel(
            domain_card,
            text=t("server_domain_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        domain_desc.pack(anchor=tk.W, pady=(2, 6))

        self.domain_var = tk.StringVar()
        self.domain_entry = StyledEntry(
            domain_card,
            textvariable=self.domain_var,
            width=60,
        )
        self.domain_entry.pack(fill=tk.X, ipady=3)

        # ─── 4. Port ve Güç Ayarları ────────────────────────────────
        port_card = CardFrame(content, padx=16, pady=10)
        port_card.pack(fill=tk.X, pady=(0, 8))

        port_title = StyledLabel(
            port_card,
            text=t("server_port_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        port_title.pack(anchor=tk.W, pady=(0, 4))

        port_row = tk.Frame(port_card, bg=theme.BG_SECONDARY)
        port_row.pack(fill=tk.X)

        port_desc = StyledLabel(
            port_row,
            text=t("server_port_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
        )
        port_desc.pack(side=tk.LEFT, padx=(0, 12))

        self.port_var = tk.StringVar(value=str(constants.CADDY_DEFAULT_PORT))
        self.port_spinbox = tk.Spinbox(
            port_row,
            from_=1,
            to=65535,
            textvariable=self.port_var,
            width=8,
            font=theme.FONT_NORMAL_BOLD,
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
            font=theme.FONT_SMALL_BOLD,
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
            cursor="hand2",
        )
        self.prevent_sleep_cb.pack(anchor=tk.W, pady=(6, 0))

        self.port_var.trace_add("write", self._on_port_change)

        # ─── Alt Butonlar ───────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 8))

        back_btn = SecondaryButton(
            footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=14,
        )
        back_btn.pack(side=tk.LEFT)

        self.next_btn = PrimaryButton(
            footer,
            text=t("btn_start_install"),
            command=self.next_page,
            width=18,
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

    def _paste_token(self) -> None:
        try:
            clip = self.clipboard_get().strip()
            if clip:
                cleaned = constants.clean_cloudflare_token(clip)
                self.token_var.set(cleaned)
        except Exception:
            pass

    def _toggle_token_visibility(self) -> None:
        self._token_visible = not self._token_visible
        if self._token_visible:
            self.token_entry.config(show="")
            self.toggle_token_btn.config(text=t("btn_hide"))
        else:
            self.token_entry.config(show="•")
            self.toggle_token_btn.config(text=t("btn_show"))

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

    def _on_folder_change(self, *_args) -> None:
        """Klasör yolu değiştiğinde canlı doğrulama durumunu günceller."""
        folder = self.folder_var.get().strip()
        if not folder:
            self.folder_status_label.config(text="")
            return
        role = self._get_current_role()
        if role == "secondary":
            self.folder_status_label.config(
                text=t("server_folder_ready_secondary"), fg=theme.SUCCESS_COLOR
            )
            return
        if os.path.isdir(folder):
            if (Path(folder) / "index.html").is_file():
                self.folder_status_label.config(
                    text=t("server_folder_valid"), fg=theme.SUCCESS_COLOR
                )
            else:
                self.folder_status_label.config(
                    text=t("server_folder_no_index_live"), fg=theme.WARNING_COLOR
                )
        else:
            self.folder_status_label.config(text="", fg=theme.FG_SECONDARY)

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

    def _update_role_descriptions(self, role: str) -> None:
        """Rol bazlı klasör açıklamasını günceller."""
        if role == "secondary":
            self.folder_desc.config(text=t("server_folder_secondary_desc"))
        else:
            self.folder_desc.config(text=t("server_folder_desc"))

    def _load_saved_data(self) -> dict:
        """Kaydedilmiş sayfa verilerini veya yapılandırmayı yükler."""
        saved = {}
        if self.controller:
            saved = self.controller.get_saved_page_data(self.PAGE_NAME) or {}

        if not saved:
            try:
                from core.config_manager import ConfigManager

                cfg_mgr = ConfigManager()
                if cfg_mgr.exists():
                    saved = cfg_mgr.load()
            except Exception:
                pass

        return saved

    def _apply_saved_data(self, saved: dict) -> None:
        """Kaydedilmiş verileri UI değişkenlerine uygular."""
        if saved:
            if saved.get("site_root_path"):
                self.folder_var.set(saved["site_root_path"])
            if saved.get("cloudflare_token"):
                token = constants.clean_cloudflare_token(saved["cloudflare_token"])
                self.token_var.set(token)
            if saved.get("public_domain") is not None:
                self.domain_var.set(saved["public_domain"])
            if saved.get("caddy_port"):
                self.port_var.set(str(saved["caddy_port"]))
            if "prevent_sleep" in saved:
                self.prevent_sleep_var.set(bool(saved["prevent_sleep"]))

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde verileri ve rol bazlı açıklamaları güncelle."""
        role = self._get_current_role()
        self._update_role_descriptions(role)

        saved = self._load_saved_data()
        self._apply_saved_data(saved)

        if role == "secondary" and not self.folder_var.get().strip():
            self.folder_var.set(str(constants.SITE_DIR))

        self._on_folder_change()
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
            try:
                Path(folder_path).mkdir(parents=True, exist_ok=True)
            except Exception:
                return False, t("err_folder_not_found", folder=folder_path)
            if not os.path.isdir(folder_path):
                return False, t("err_folder_not_found", folder=folder_path)
        else:
            if not os.path.isdir(folder_path):
                return False, t("err_folder_not_found", folder=folder_path)

            index_path = Path(folder_path) / "index.html"
            if not index_path.is_file():
                return False, t("err_no_index", index_path=index_path)

        token = constants.clean_cloudflare_token(self.token_var.get().strip())
        self.token_var.set(token)
        if not token:
            return False, t("err_no_token")
        if not re.match(constants.CLOUDFLARE_TOKEN_REGEX, token):
            return False, t("err_invalid_token")

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
            "cloudflare_token": constants.clean_cloudflare_token(self.token_var.get().strip()),
            "public_domain": self.domain_var.get().strip(),
            "caddy_port": int(self.port_var.get() or constants.CADDY_DEFAULT_PORT),
            "prevent_sleep": bool(self.prevent_sleep_var.get()),
        }