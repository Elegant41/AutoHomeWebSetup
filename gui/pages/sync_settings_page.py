"""
Senkronizasyon Ayarları sayfası.

Merkez/Yedek seçimi ve koşullu Syncthing Device ID girişi içerir.
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
from utils.logger import get_logger
from utils.i18n import t

logger = get_logger(__name__)


class SyncSettingsPage(BasePage):
    """3. Adım: Senkronizasyon Ayarları (Merkez/Yedek + Device ID)."""

    PAGE_NAME = "sync_settings"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # ─── Başlık ─────────────────────────────────────────────────
        header = HeaderFrame(
            self,
            title=t("sync_title"),
            subtitle=t("sync_subtitle"),
        )
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(theme.PADDING_LARGE, theme.PADDING_MEDIUM))

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=theme.PADDING_MEDIUM)

        # ─── Rol Seçimi ─────────────────────────────────────────────
        role_card = CardFrame(content)
        role_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        role_title = StyledLabel(
            role_card,
            text=t("sync_role_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        role_title.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

        self.role_var = tk.StringVar(value="primary")

        # Merkez seçeneği
        primary_frame = tk.Frame(role_card, bg=theme.BG_SECONDARY)
        primary_frame.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        self.primary_radio = tk.Radiobutton(
            primary_frame,
            text=t("sync_role_primary"),
            variable=self.role_var,
            value="primary",
            command=self._on_role_change,
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            selectcolor=theme.BG_TERTIARY,
            activebackground=theme.BG_SECONDARY,
            activeforeground=theme.FG_COLOR,
            highlightthickness=0,
        )
        self.primary_radio.pack(anchor=tk.W)

        primary_desc = StyledLabel(
            primary_frame,
            text=t("sync_primary_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=550,
            justify=tk.LEFT,
        )
        primary_desc.pack(anchor=tk.W, padx=(theme.PADDING_LARGE, 0), pady=(2, theme.PADDING_SMALL))

        # Yedek seçeneği
        secondary_frame = tk.Frame(role_card, bg=theme.BG_SECONDARY)
        secondary_frame.pack(fill=tk.X)

        self.secondary_radio = tk.Radiobutton(
            secondary_frame,
            text=t("sync_role_secondary"),
            variable=self.role_var,
            value="secondary",
            command=self._on_role_change,
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            selectcolor=theme.BG_TERTIARY,
            activebackground=theme.BG_SECONDARY,
            activeforeground=theme.FG_COLOR,
            highlightthickness=0,
        )
        self.secondary_radio.pack(anchor=tk.W)

        secondary_desc = StyledLabel(
            secondary_frame,
            text=t("sync_secondary_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=550,
            justify=tk.LEFT,
        )
        secondary_desc.pack(anchor=tk.W, padx=(theme.PADDING_LARGE, 0), pady=(2, 0))

        # ─── Device ID & Join Key Girişi (Yedek seçilirse görünür) ──
        self.device_id_card = CardFrame(content)
        # Başlangıçta gizli (Merkez seçiliyken)

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
            wraplength=550,
            justify=tk.LEFT,
        )
        join_key_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_XS))

        self.join_key_var = tk.StringVar()
        self.join_key_entry = StyledEntry(
            self.device_id_card,
            textvariable=self.join_key_var,
            width=60,
        )
        self.join_key_entry.pack(fill=tk.X, pady=(0, 2))

        self.join_key_status = StyledLabel(
            self.device_id_card,
            text="",
            font=theme.FONT_SMALL,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.join_key_status.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))
        self.join_key_var.trace_add("write", self._on_join_key_change)

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
            wraplength=550,
            justify=tk.LEFT,
        )
        device_id_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_XS))

        self.device_id_var = tk.StringVar()
        self.device_id_entry = StyledEntry(
            self.device_id_card,
            textvariable=self.device_id_var,
            width=60,
        )
        self.device_id_entry.pack(fill=tk.X)

        self.device_id_hint = StyledLabel(
            self.device_id_card,
            text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFF-GGGGGGG-HHHHHHH",
            font=theme.FONT_SMALL,
            fg=theme.FG_DISABLED,
            bg=theme.BG_SECONDARY,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(theme.PADDING_XS, 0))

        # ─── Alt Butonlar ───────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=theme.PADDING_MEDIUM)

        back_btn = SecondaryButton(
            footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=12,
        )
        back_btn.pack(side=tk.LEFT)

        next_btn = PrimaryButton(
            footer,
            text=t("btn_next"),
            command=self._on_install_clicked,
            width=14,
        )
        next_btn.pack(side=tk.RIGHT)

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def _on_role_change(self) -> None:
        """Rol değiştiğinde Device ID alanını göster/gizle."""
        if self.role_var.get() == "secondary":
            self.device_id_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))
        else:
            self.device_id_card.pack_forget()
            self.device_id_var.set("")
            self.join_key_var.set("")
            self.join_key_status.config(text="")

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
        if self.controller:
            saved = self.controller.get_saved_page_data(self.PAGE_NAME)
            if saved:
                if saved.get("node_role"):
                    self.role_var.set(saved["node_role"])
                if saved.get("primary_device_id"):
                    self.device_id_var.set(saved["primary_device_id"])
                if saved.get("join_key"):
                    self.join_key_var.set(saved["join_key"])

        # Rol durumuna göre Device ID alanını ayarla
        self._on_role_change()

    def validate(self) -> tuple[bool, str]:
        """Sayfa geçiş validasyonu."""
        role = self.role_var.get()

        if role == "secondary":
            raw_join = self.join_key_var.get().strip()
            device_id = self.device_id_var.get().strip()

            # Kullanıcı yanlışlıkla Join Key'i Device ID kutusuna yapıştırdıysa destekle
            if device_id.startswith(constants.JOIN_KEY_PREFIX) and not raw_join:
                self.join_key_var.set(device_id)
                raw_join = device_id
                device_id = self.device_id_var.get().strip()

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
            "primary_device_id": self.device_id_var.get().strip(),
            "join_key": self.join_key_var.get().strip(),
        }