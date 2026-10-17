"""
Senkronizasyon Ayarları sayfası.

Etkileşimli Merkez/Yedek rol seçim kartları, tek tıkla "Yapıştır" destekli
Küme Katılım Kodu (Join Key) ve canlı doğrulamalı Syncthing Device ID girişi içerir.
"""

import re
import tkinter as tk

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

logger = get_logger(__name__)


class SyncSettingsPage(BasePage):
    """2. Adım: Senkronizasyon Ayarları (Merkez/Yedek + Join Key / Device ID)."""

    PAGE_NAME = "sync_settings"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # ─── Başlık ─────────────────────────────────────────────────
        header = HeaderFrame(
            self,
            title=t("sync_title"),
            subtitle=t("sync_subtitle"),
        )
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(16, 8))

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=(0, 8))

        # ─── Rol Seçimi (Etkileşimli Kartlar) ───────────────────────
        self.role_var = tk.StringVar(value="primary")

        roles_container = tk.Frame(content, bg=theme.BG_COLOR)
        roles_container.pack(fill=tk.X, pady=(0, 10))
        roles_container.grid_columnconfigure(0, weight=1, uniform="role_col")
        roles_container.grid_columnconfigure(1, weight=1, uniform="role_col")

        # 1. Merkez Bilgisayar Kartı
        self.primary_card = CardFrame(roles_container, padx=16, pady=12)
        self.primary_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.primary_radio = tk.Radiobutton(
            self.primary_card,
            text=t("sync_role_primary"),
            variable=self.role_var,
            value="primary",
            command=self._on_role_change,
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            selectcolor=theme.BG_TERTIARY,
            activebackground=theme.BG_SECONDARY,
            activeforeground=theme.ACCENT_COLOR,
            highlightthickness=0,
            cursor="hand2",
        )
        self.primary_radio.pack(anchor=tk.W)

        primary_desc = StyledLabel(
            self.primary_card,
            text=t("sync_primary_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=350,
            justify=tk.LEFT,
        )
        primary_desc.pack(anchor=tk.W, pady=(4, 0))

        # Kartın herhangi bir yerine tıklayınca Merkez seçilsin
        for widget in (self.primary_card, primary_desc):
            widget.bind("<Button-1>", lambda _e: self._select_role("primary"))

        # 2. Yedek Bilgisayar Kartı
        self.secondary_card = CardFrame(roles_container, padx=16, pady=12)
        self.secondary_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.secondary_radio = tk.Radiobutton(
            self.secondary_card,
            text=t("sync_role_secondary"),
            variable=self.role_var,
            value="secondary",
            command=self._on_role_change,
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            selectcolor=theme.BG_TERTIARY,
            activebackground=theme.BG_SECONDARY,
            activeforeground=theme.ACCENT_COLOR,
            highlightthickness=0,
            cursor="hand2",
        )
        self.secondary_radio.pack(anchor=tk.W)

        secondary_desc = StyledLabel(
            self.secondary_card,
            text=t("sync_secondary_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=350,
            justify=tk.LEFT,
        )
        secondary_desc.pack(anchor=tk.W, pady=(4, 0))

        for widget in (self.secondary_card, secondary_desc):
            widget.bind("<Button-1>", lambda _e: self._select_role("secondary"))

        # ─── Device ID & Join Key Girişi (Yedek seçilirse görünür) ──
        self.device_id_card = CardFrame(content, padx=16, pady=12)

        join_key_title = StyledLabel(
            self.device_id_card,
            text=t("sync_join_key_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_SECONDARY,
        )
        join_key_title.pack(anchor=tk.W, pady=(0, 2))

        join_key_desc = StyledLabel(
            self.device_id_card,
            text=t("sync_join_key_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        join_key_desc.pack(anchor=tk.W, pady=(0, 6))

        join_row = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)
        join_row.pack(fill=tk.X)

        paste_join_btn = SecondaryButton(
            join_row,
            text=t("btn_paste"),
            command=self._paste_join_key,
            width=10,
        )
        paste_join_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.join_key_var = tk.StringVar()
        self.join_key_entry = StyledEntry(
            join_row,
            textvariable=self.join_key_var,
            font=theme.FONT_MONO_SMALL,
            width=60,
        )
        self.join_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        self.join_key_status = StyledLabel(
            self.device_id_card,
            text="",
            font=theme.FONT_SMALL_BOLD,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.join_key_status.pack(anchor=tk.W, pady=(4, 8))
        self.join_key_var.trace_add("write", self._on_join_key_change)

        # Ayırıcı çizgi
        tk.Frame(self.device_id_card, bg=theme.CARD_BORDER, height=1).pack(fill=tk.X, pady=(0, 8))

        device_id_title = StyledLabel(
            self.device_id_card,
            text=t("sync_device_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_id_title.pack(anchor=tk.W, pady=(0, 2))

        device_id_desc = StyledLabel(
            self.device_id_card,
            text=t("sync_device_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        device_id_desc.pack(anchor=tk.W, pady=(0, 6))

        dev_row = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)
        dev_row.pack(fill=tk.X)

        paste_dev_btn = SecondaryButton(
            dev_row,
            text=t("btn_paste"),
            command=self._paste_device_id,
            width=10,
        )
        paste_dev_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.device_id_var = tk.StringVar()
        self.device_id_entry = StyledEntry(
            dev_row,
            textvariable=self.device_id_var,
            font=theme.FONT_MONO_SMALL,
            width=60,
        )
        self.device_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        self.device_id_hint = StyledLabel(
            self.device_id_card,
            text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
            font=theme.FONT_SMALL,
            fg=theme.FG_DISABLED,
            bg=theme.BG_SECONDARY,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(4, 0))
        self.device_id_var.trace_add("write", self._on_device_id_change)

        # ─── Alt Butonlar ───────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 8))

        back_btn = SecondaryButton(
            footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=14,
        )
        back_btn.pack(side=tk.LEFT)

        next_btn = PrimaryButton(
            footer,
            text=t("btn_next"),
            command=self._on_install_clicked,
            width=16,
        )
        next_btn.pack(side=tk.RIGHT)

        self._on_role_change()

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def _select_role(self, role: str) -> None:
        self.role_var.set(role)
        self._on_role_change()

    def _paste_join_key(self) -> None:
        try:
            clip = self.clipboard_get().strip()
            if clip:
                self.join_key_var.set(clip)
        except Exception:
            pass

    def _paste_device_id(self) -> None:
        try:
            clip = self.clipboard_get().strip()
            if clip:
                if clip.startswith(constants.JOIN_KEY_PREFIX):
                    self.join_key_var.set(clip)
                else:
                    self.device_id_var.set(clip)
        except Exception:
            pass

    def _on_role_change(self) -> None:
        """Rol değiştiğinde kart kenarlıklarını ve Device ID alanını günceller."""
        role = self.role_var.get()
        self.primary_card.set_active(role == "primary")
        self.secondary_card.set_active(role == "secondary")

        if role == "secondary":
            self.device_id_card.pack(fill=tk.X, pady=(0, 8))
        else:
            self.device_id_card.pack_forget()
            self.device_id_var.set("")
            self.join_key_var.set("")
            self.join_key_status.config(text="")

    def _on_device_id_change(self, *_args) -> None:
        """Device ID yazıldığında veya yapıştırıldığında canlı format kontrolü yapar."""
        val = self.device_id_var.get().strip().upper()
        if not val:
            self.device_id_hint.config(
                text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
                fg=theme.FG_DISABLED,
            )
            return

        # Yanlışlıkla Join Key yapıştırıldıysa otomatik üst kutuya aktar
        if val.startswith(constants.JOIN_KEY_PREFIX) and not self.join_key_var.get().strip():
            raw = self.device_id_var.get().strip()
            self.device_id_var.set("")
            self.join_key_var.set(raw)
            return

        if re.match(constants.DEVICE_ID_REGEX, val):
            self.device_id_hint.config(text=t("sync_device_valid"), fg=theme.SUCCESS_COLOR)
        else:
            self.device_id_hint.config(text=t("sync_device_invalid_live"), fg=theme.WARNING_COLOR)

    def _on_join_key_change(self, *_args) -> None:
        """Join Key girildiğinde otomatik çöz ve alanları doldur."""
        raw_key = self.join_key_var.get().strip()
        if not raw_key:
            self.join_key_status.config(text="")
            return

        try:
            from core.models import InstallConfig

            payload = InstallConfig.parse_join_key(raw_key)
            if not payload:
                self.join_key_status.config(text=t("err_invalid_join_key"), fg=theme.ERROR_COLOR)
                return

            dev_id = payload.get("primary_device_id", "")
            if dev_id:
                self.device_id_var.set(dev_id)

            if self.controller:
                existing_server = dict(self.controller.get_saved_page_data("server_settings") or {})
                if payload.get("cloudflare_token"):
                    existing_server["cloudflare_token"] = payload["cloudflare_token"]
                if payload.get("caddy_port"):
                    existing_server["caddy_port"] = int(payload["caddy_port"])
                if payload.get("public_domain") is not None:
                    existing_server["public_domain"] = payload.get("public_domain", "")
                if not existing_server.get("site_root_path"):
                    existing_server["site_root_path"] = str(constants.SITE_DIR)
                self.controller.collect_page_data("server_settings", existing_server)

            self.join_key_status.config(text=t("sync_join_key_applied"), fg=theme.SUCCESS_COLOR)
        except Exception:
            self.join_key_status.config(text=t("err_invalid_join_key"), fg=theme.ERROR_COLOR)

    def _on_install_clicked(self) -> None:
        """İleri butonuna tıklandığında."""
        self.next_page()

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde verileri geri yükle."""
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

        if saved:
            if saved.get("node_role") in ("primary", "secondary"):
                self.role_var.set(saved["node_role"])
            if saved.get("primary_device_id"):
                self.device_id_var.set(saved["primary_device_id"])
            if saved.get("join_key"):
                self.join_key_var.set(saved["join_key"])

        self._on_role_change()

    def validate(self) -> tuple[bool, str]:
        """Sayfa geçiş validasyonu."""
        role = self.role_var.get()

        if role == "secondary":
            raw_join = self.join_key_var.get().strip()
            device_id = self.device_id_var.get().strip().upper()

            if device_id.startswith(constants.JOIN_KEY_PREFIX) and not raw_join:
                self.join_key_var.set(self.device_id_var.get().strip())
                raw_join = self.join_key_var.get().strip()
                device_id = self.device_id_var.get().strip().upper()

            if raw_join:
                from core.models import InstallConfig

                if not InstallConfig.parse_join_key(raw_join):
                    return False, t("err_invalid_join_key")

            if not device_id:
                return False, t("err_no_device_id")
            if not re.match(constants.DEVICE_ID_REGEX, device_id):
                return False, t("err_invalid_device_id")

        return True, ""

    def get_data(self) -> dict:
        """Sayfa verilerini döndürür."""
        return {
            "node_role": self.role_var.get(),
            "primary_device_id": self.device_id_var.get().strip().upper(),
            "join_key": self.join_key_var.get().strip(),
        }