"""
Bitiş sayfası.

Başarı mesajı, Device ID gösterimi + kopyala butonu ve
"Yedek Ekle" butonu (Merkez ise) içerir.
"""

import tkinter as tk

from gui import theme
from gui.base_page import BasePage
from gui.widgets import (
    CardFrame,
    PrimaryButton,
    SecondaryButton,
    StyledLabel,
)
from gui.dialogs.node_manager_dialog import NodeManagerDialog
from utils.logger import get_logger
from utils.i18n import t

logger = get_logger(__name__)


class FinishPage(BasePage):
    """5. Adım: Bitiş + Device ID + Canlı Durum Paneli."""

    PAGE_NAME = "finish"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.local_device_id = ""
        self.join_key = ""
        self.node_role = "primary"

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=theme.PADDING_MEDIUM)

        # ─── Başarı Mesajı ──────────────────────────────────────────
        success_frame = tk.Frame(content, bg=theme.BG_COLOR)
        success_frame.pack(fill=tk.X, pady=(4, 8))

        title_row = tk.Frame(success_frame, bg=theme.BG_COLOR)
        title_row.pack()

        success_icon = StyledLabel(
            title_row,
            text="✓ ",
            font=("Segoe UI", 22, "bold"),
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_COLOR,
        )
        success_icon.pack(side=tk.LEFT)

        success_title = StyledLabel(
            title_row,
            text=t("finish_title"),
            font=theme.FONT_TITLE,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_COLOR,
        )
        success_title.pack(side=tk.LEFT)

        success_subtitle = StyledLabel(
            success_frame,
            text=t("finish_success_msg"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=600,
            justify=tk.CENTER,
        )
        success_subtitle.pack(pady=(2, 4))

        # ─── Device ID & Join Key Kartı ─────────────────────────────
        self.device_id_card = CardFrame(content)
        self.device_id_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        device_id_title = StyledLabel(
            self.device_id_card,
            text=t("finish_device_id_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_id_title.pack(anchor=tk.W, pady=(0, 2))

        device_id_row = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)
        device_id_row.pack(fill=tk.X)

        self.device_id_label = StyledLabel(
            device_id_row,
            text=t("finish_loading"),
            font=theme.FONT_MONO_SMALL,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.device_id_label.pack(side=tk.LEFT, padx=(0, theme.PADDING_SMALL))

        copy_btn = SecondaryButton(
            device_id_row,
            text=t("btn_copy"),
            command=self._copy_device_id,
            width=12,
        )
        copy_btn.pack(side=tk.RIGHT)

        self.device_id_hint = StyledLabel(
            self.device_id_card,
            text=t("finish_primary_hint"),
            font=theme.FONT_SMALL,
            fg=theme.FG_DISABLED,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(2, 0))

        # Küme Katılım Anahtarı satırı (Merkez düğümde görünür)
        self.join_key_frame = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)
        self.join_key_frame.pack(fill=tk.X, pady=(6, 0))

        join_key_lbl = StyledLabel(
            self.join_key_frame,
            text=f"{t('finish_join_key_title')}: {t('finish_join_key_desc')}",
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=480,
            justify=tk.LEFT,
        )
        join_key_lbl.pack(side=tk.LEFT)

        copy_join_btn = SecondaryButton(
            self.join_key_frame,
            text=t("btn_copy"),
            command=self._copy_join_key,
            width=12,
        )
        copy_join_btn.pack(side=tk.RIGHT)

        # ─── Canlı Sistem ve Servis Durumu Kartı ────────────────────
        self.health_card = CardFrame(content)
        self.health_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        health_header = tk.Frame(self.health_card, bg=theme.BG_SECONDARY)
        health_header.pack(fill=tk.X, pady=(0, 4))

        health_title = StyledLabel(
            health_header,
            text=t("health_card_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        health_title.pack(side=tk.LEFT)

        refresh_btn = SecondaryButton(
            health_header,
            text=t("btn_refresh_status"),
            command=self.refresh_health_status,
            width=16,
        )
        refresh_btn.pack(side=tk.RIGHT)

        self.health_status_label = StyledLabel(
            self.health_card,
            text=t("finish_loading"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            justify=tk.LEFT,
        )
        self.health_status_label.pack(anchor=tk.W)

        # ─── Siteyi Aç ve Ayarlar Kartı ─────────────────────────────
        open_site_card = CardFrame(content)
        open_site_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))

        open_site_desc = StyledLabel(
            open_site_card,
            text=t("finish_open_site_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
        )
        open_site_desc.pack(anchor=tk.W, pady=(0, theme.PADDING_XS))

        site_btn_row = tk.Frame(open_site_card, bg=theme.BG_SECONDARY)
        site_btn_row.pack(fill=tk.X)

        open_site_btn = PrimaryButton(
            site_btn_row,
            text=t("btn_open_site_browser"),
            command=self._open_website,
            width=26,
        )
        open_site_btn.pack(side=tk.LEFT, padx=(0, theme.PADDING_SMALL))

        settings_btn = SecondaryButton(
            site_btn_row,
            text=t("btn_settings"),
            command=self._open_settings,
            width=18,
        )
        settings_btn.pack(side=tk.LEFT)

        # ─── Yedek Ekle Kartı (sadece Merkez için) ───────────────────
        self.node_manager_card = CardFrame(content)
        # Başlangıçta gizli

        node_row = tk.Frame(self.node_manager_card, bg=theme.BG_SECONDARY)
        node_row.pack(fill=tk.X)

        node_manager_desc = StyledLabel(
            node_row,
            text=t("finish_device_id_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=460,
            justify=tk.LEFT,
        )
        node_manager_desc.pack(side=tk.LEFT)

        add_node_btn = SecondaryButton(
            node_row,
            text=t("btn_add_node"),
            command=self._open_node_manager,
            width=16,
        )
        add_node_btn.pack(side=tk.RIGHT)

        # ─── Kapat Butonu ───────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=theme.PADDING_SMALL)

        close_btn = PrimaryButton(
            footer,
            text=t("btn_close"),
            command=self._close_window,
            width=14,
        )
        close_btn.pack()

    def _open_website(self) -> None:
        """Yerel web sitesini veya ayarlanmışsa internet sitesini varsayılan tarayıcıda açar."""
        import webbrowser
        port = 80
        url = ""
        try:
            from core.config_manager import ConfigManager
            saved = ConfigManager().load()
            port = saved.get("caddy_port", 80)
            url = saved.get("public_domain", "").strip()
        except Exception:
            pass

        if not url:
            url = "http://localhost" if port == 80 else f"http://localhost:{port}"
        elif not url.startswith("http"):
            url = f"https://{url}"

        webbrowser.open(url)

    def _open_settings(self) -> None:
        """Ayarlar diyaloğunu açar."""
        from gui.dialogs.settings_dialog import SettingsDialog
        SettingsDialog(self, self.controller)

    def _copy_device_id(self) -> None:
        """Device ID'yi panoya kopyalar."""
        if self.local_device_id:
            self.clipboard_clear()
            self.clipboard_append(self.local_device_id)
            self._display_info(t("msg_copied_title"), t("msg_copied_device_id"))

    def _copy_join_key(self) -> None:
        """Küme Katılım Anahtarını panoya kopyalar."""
        if self.join_key:
            self.clipboard_clear()
            self.clipboard_append(self.join_key)
            self._display_info(t("msg_copied_title"), t("msg_copied_join_key"))

    def _open_node_manager(self) -> None:
        """Node manager diyaloğunu açar."""
        NodeManagerDialog(self, self.controller)

    def _close_window(self) -> None:
        """Uygulamayı kapatır."""
        self.controller.destroy()

    def set_device_id(self, device_id: str) -> None:
        """Device ID'yi ayarlar ve gösterir."""
        self.local_device_id = device_id
        if device_id:
            self.device_id_label.config(text=device_id)

    def set_node_role(self, role: str) -> None:
        """Node rolünü ayarlar. 'secondary' ise Yedek Ekle kartını gizler."""
        self.node_role = role
        if role == "secondary":
            self.node_manager_card.pack_forget()
            self.join_key_frame.pack_forget()
            self.device_id_hint.config(text=t("finish_secondary_hint"))
        else:
            self.node_manager_card.pack(fill=tk.X, pady=(0, theme.PADDING_SMALL))
            if self.join_key:
                self.join_key_frame.pack(fill=tk.X, pady=(6, 0))
            self.device_id_hint.config(text=t("finish_primary_hint"))

    def refresh_health_status(self) -> None:
        """Servislerin canlı çalışma durumunu sorgular ve etiketi günceller."""
        if not self.controller or not hasattr(self.controller, "installer_engine"):
            return
        try:
            health = self.controller.installer_engine.get_system_health()
            caddy_txt = t("health_running") if health.get("caddy_running") else t("health_stopped")
            cf_txt = t("health_running") if health.get("cloudflared_running") else t("health_stopped")
            st_txt = t("health_running") if health.get("syncthing_running") else t("health_stopped")
            peers = health.get("paired_devices", 0)

            summary = (
                f"Caddy: {caddy_txt}   |   "
                f"Cloudflared: {cf_txt}   |   "
                f"Syncthing: {st_txt}   |   "
                f"{t('health_paired_nodes', count=peers)}"
            )
            self.health_status_label.config(text=summary)
        except Exception as e:
            logger.debug(f"Sağlık durumu okunamadı: {e}")

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde verileri yükle."""
        if self.controller:
            config = self.controller.build_install_config()
            role = getattr(config, "node_role", "primary")
            role_str = role.value if hasattr(role, "value") else str(role)

            # Device ID'yi sırasıyla yükle
            device_id = getattr(config, "local_device_id", "") or ""
            saved = {}
            try:
                from core.config_manager import ConfigManager
                saved = ConfigManager().load()
                if not device_id:
                    device_id = saved.get("local_device_id", "")
            except Exception as e:
                logger.warning(f"Kayıtlı konfigürasyondan Device ID okunamadı: {e}")

            if not device_id and hasattr(self.controller, "installer_engine"):
                try:
                    device_id = self.controller.installer_engine.syncthing_service.get_device_id()
                except Exception as e:
                    logger.warning(f"Syncthing servisinden Device ID okunamadı: {e}")

            # Küme Katılım Anahtarı oluştur
            token = getattr(config, "cloudflare_token", "") or saved.get("cloudflare_token", "")
            port = getattr(config, "caddy_port", 80) or saved.get("caddy_port", 80)
            domain = getattr(config, "public_domain", "") or saved.get("public_domain", "")
            if device_id and token:
                try:
                    from core.models import InstallConfig
                    self.join_key = InstallConfig.generate_join_key(
                        primary_device_id=device_id,
                        cloudflare_token=token,
                        caddy_port=int(port),
                        public_domain=domain,
                    )
                except Exception:
                    self.join_key = ""

            self.set_device_id(device_id)
            self.set_node_role(role_str)
            self.refresh_health_status()