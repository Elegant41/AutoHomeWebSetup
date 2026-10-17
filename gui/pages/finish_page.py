"""
Bitiş ve Canlı Durum Paneli sayfası.

Başarı mesajı, Cihaz ID / Küme Katılım Kodu gösterimi (satır içi kopyalandı animasyonlu),
4 kutulu canlı servis sağlık paneli (Caddy, Cloudflared, Syncthing, Eşleşen Cihaz)
ve Merkez düğüm için "+ Yedek Bilgisayar Ekle" yönetimi içerir.
"""

import threading
import tkinter as tk

from gui import theme
from gui.base_page import BasePage
from gui.dialogs.node_manager_dialog import NodeManagerDialog
from gui.widgets import (
    CardFrame,
    PrimaryButton,
    SecondaryButton,
    StyledLabel,
)
from utils import constants
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


class FinishPage(BasePage):
    """5. Adım: Bitiş + Cihaz ID + Canlı Durum Paneli."""

    PAGE_NAME = "finish"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.local_device_id = ""
        self.join_key = ""
        self.node_role = "primary"
        self._auto_refresh_job = None
        self._is_active = False

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=(10, 8))

        # ─── Başarı Başlığı ─────────────────────────────────────────
        success_frame = tk.Frame(self, bg=theme.BG_COLOR)
        success_frame.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(10, 2), before=content)

        title_row = tk.Frame(success_frame, bg=theme.BG_COLOR)
        title_row.pack(anchor=tk.W)

        success_icon = StyledLabel(
            title_row,
            text="✓ ",
            font=("Segoe UI", 20, "bold"),
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
            wraplength=760,
            justify=tk.LEFT,
        )
        success_subtitle.pack(anchor=tk.W, pady=(2, 0))

        # ─── 1. Canlı Sistem ve Servis Durumu Kartı (4 Kutulu Grid) ─
        self.health_card = CardFrame(content, padx=16, pady=12)
        self.health_card.pack(fill=tk.X, pady=(0, 8))

        health_header = tk.Frame(self.health_card, bg=theme.BG_SECONDARY)
        health_header.pack(fill=tk.X, pady=(0, 8))

        refresh_btn = SecondaryButton(
            health_header,
            text=t("btn_refresh_status"),
            command=self.refresh_health_status,
            width=16,
        )
        refresh_btn.pack(side=tk.RIGHT)

        health_title = StyledLabel(
            health_header,
            text=t("health_card_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        health_title.pack(side=tk.LEFT)

        # 4'lü Durum Kutuları
        self.health_grid = tk.Frame(self.health_card, bg=theme.BG_SECONDARY)
        self.health_grid.pack(fill=tk.X)
        for col in range(4):
            self.health_grid.grid_columnconfigure(col, weight=1, uniform="health_col")

        self.caddy_box, self.caddy_status_lbl = self._create_health_box(0, t("health_col_caddy"))
        self.cf_box, self.cf_status_lbl = self._create_health_box(1, t("health_col_cloudflared"))
        self.st_box, self.st_status_lbl = self._create_health_box(2, t("health_col_syncthing"))
        self.nodes_box, self.nodes_status_lbl = self._create_health_box(3, t("health_col_nodes"))

        self.health_status_label = self.nodes_status_lbl

        # ─── 2. Cihaz ID & Küme Katılım Kodu Kartı ──────────────────
        self.device_id_card = CardFrame(content, padx=16, pady=12)
        self.device_id_card.pack(fill=tk.X, pady=(0, 8))

        device_id_title = StyledLabel(
            self.device_id_card,
            text=t("finish_device_id_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_id_title.pack(anchor=tk.W, pady=(0, 4))

        device_id_row = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)
        device_id_row.pack(fill=tk.X)

        self.copy_id_btn = SecondaryButton(
            device_id_row,
            text=t("btn_copy"),
            command=self._copy_device_id,
            width=14,
        )
        self.copy_id_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.device_id_label = StyledLabel(
            device_id_row,
            text=t("finish_loading"),
            font=theme.FONT_MONO_SMALL,
            fg=theme.ACCENT_COLOR,
            bg=theme.ENTRY_BG,
            padx=10,
            pady=6,
            anchor=tk.W,
        )
        self.device_id_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.device_id_hint = StyledLabel(
            self.device_id_card,
            text=t("finish_primary_hint"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(6, 0))

        # Küme Katılım Anahtarı satırı (Sadece Merkez düğümde gösterilir)
        self.join_key_frame = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)

        self.copy_join_btn = SecondaryButton(
            self.join_key_frame,
            text=t("btn_copy_join_key"),
            command=self._copy_join_key,
            width=22,
        )
        self.copy_join_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        join_key_lbl = StyledLabel(
            self.join_key_frame,
            text=f"• {t('finish_join_key_title')}: {t('finish_join_key_desc')}",
            font=theme.FONT_SMALL,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_SECONDARY,
            wraplength=520,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        join_key_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── 3. Hızlı İşlemler: Siteyi Aç, Syncthing Paneli ve Ayarlar ─
        open_site_card = CardFrame(content, padx=16, pady=12)
        open_site_card.pack(fill=tk.X, pady=(0, 8))

        open_site_desc = StyledLabel(
            open_site_card,
            text=t("finish_open_site_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        open_site_desc.pack(anchor=tk.W, pady=(0, 8))

        site_btn_row = tk.Frame(open_site_card, bg=theme.BG_SECONDARY)
        site_btn_row.pack(fill=tk.X)

        open_site_btn = PrimaryButton(
            site_btn_row,
            text=t("btn_open_site_browser"),
            command=self._open_website,
            width=24,
        )
        open_site_btn.pack(side=tk.LEFT, padx=(0, theme.PADDING_SMALL))

        open_st_btn = SecondaryButton(
            site_btn_row,
            text=t("btn_open_syncthing"),
            command=self._open_syncthing_ui,
            width=18,
        )
        open_st_btn.pack(side=tk.LEFT, padx=(0, theme.PADDING_SMALL))

        settings_btn = SecondaryButton(
            site_btn_row,
            text=t("btn_settings"),
            command=self._open_settings,
            width=16,
        )
        settings_btn.pack(side=tk.LEFT)

        # ─── 4. Yedek Ekle Kartı (Sadece Merkez düğüm için) ─────────
        self.node_manager_card = CardFrame(content, padx=16, pady=12, border_color=theme.ACCENT_COLOR)

        node_row = tk.Frame(self.node_manager_card, bg=theme.BG_SECONDARY)
        node_row.pack(fill=tk.X)

        add_node_btn = PrimaryButton(
            node_row,
            text=t("btn_add_node"),
            command=self._open_node_manager,
            width=22,
        )
        add_node_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        node_manager_desc = StyledLabel(
            node_row,
            text=t("finish_device_id_desc"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            wraplength=500,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        node_manager_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── Alt Butonlar (Ana Ekran & Kapat) ───────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 6))

        home_btn = SecondaryButton(
            footer,
            text=t("btn_home"),
            command=self._go_home,
            width=14,
        )
        home_btn.pack(side=tk.LEFT)

        close_btn = PrimaryButton(
            footer,
            text=t("btn_close"),
            command=self._close_window,
            width=14,
        )
        close_btn.pack(side=tk.RIGHT)

    def _create_health_box(self, col: int, title_text: str) -> tuple[tk.Frame, StyledLabel]:
        """Sağlık panelinde tek bir servis kutusu oluşturur ve (kutu, durum etiketi) döndürür."""
        pad_left = 0 if col == 0 else 4
        pad_right = 0 if col == 3 else 4

        box = tk.Frame(
            self.health_grid,
            bg=theme.ENTRY_BG,
            padx=12,
            pady=8,
            highlightthickness=1,
            highlightbackground=theme.CARD_BORDER,
            highlightcolor=theme.CARD_BORDER,
        )
        box.grid(row=0, column=col, sticky="nsew", padx=(pad_left, pad_right))

        title_lbl = StyledLabel(
            box,
            text=title_text,
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.ENTRY_BG,
        )
        title_lbl.pack(anchor=tk.W)

        status_lbl = StyledLabel(
            box,
            text=t("finish_loading"),
            font=theme.FONT_NORMAL_BOLD,
            fg=theme.FG_SECONDARY,
            bg=theme.ENTRY_BG,
        )
        status_lbl.pack(anchor=tk.W, pady=(3, 0))
        return box, status_lbl

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

    def _open_syncthing_ui(self) -> None:
        """Yerel Syncthing yönetim arayüzünü tarayıcıda açar."""
        import webbrowser

        gui_port = constants.SYNCTHING_GUI_PORT
        try:
            from core.config_manager import ConfigManager

            saved = ConfigManager().load()
            gui_port = saved.get("syncthing_gui_port", constants.SYNCTHING_GUI_PORT)
        except Exception:
            pass
        webbrowser.open(f"http://127.0.0.1:{gui_port}")

    def _open_settings(self) -> None:
        """Ayarlar diyaloğunu açar."""
        from gui.dialogs.settings_dialog import SettingsDialog

        SettingsDialog(self, self.controller)

    def _flash_button_copied(self, btn: SecondaryButton, original_key: str) -> None:
        """Kopyala butonunda 2 saniyeliğine yeşil '✓ Kopyalandı' geri bildirimi gösterir."""
        btn.config(text=t("btn_copied_inline"), fg=theme.SUCCESS_COLOR)
        self.after(
            2000,
            lambda: btn.config(text=t(original_key), fg=theme.FG_COLOR) if btn.winfo_exists() else None,
        )

    def _copy_device_id(self) -> None:
        """Device ID'yi panoya kopyalar."""
        if self.local_device_id:
            self.clipboard_clear()
            self.clipboard_append(self.local_device_id)
            self._flash_button_copied(self.copy_id_btn, "btn_copy")

    def _copy_join_key(self) -> None:
        """Küme Katılım Anahtarını panoya kopyalar."""
        if self.join_key:
            self.clipboard_clear()
            self.clipboard_append(self.join_key)
            self._flash_button_copied(self.copy_join_btn, "btn_copy_join_key")

    def _open_node_manager(self) -> None:
        """Node manager diyaloğunu açar (Sadece Merkez düğümde)."""
        if self.node_role == "secondary":
            return
        NodeManagerDialog(self, self.controller)

    def _go_home(self) -> None:
        """Hoşgeldiniz ekranına döner."""
        if self.controller:
            self.controller.go_to_page("welcome")

    def _close_window(self) -> None:
        """Uygulamayı kapatır."""
        self.controller.destroy()

    def set_device_id(self, device_id: str) -> None:
        """Device ID'yi ayarlar ve gösterir."""
        self.local_device_id = device_id
        if device_id:
            self.device_id_label.config(text=device_id)

    def set_node_role(self, role: str) -> None:
        """Node rolünü ayarlar. 'secondary' ise Yedek Ekle kartını ve Join Key'i gizler."""
        self.node_role = role
        if role == "secondary":
            self.node_manager_card.pack_forget()
            self.join_key_frame.pack_forget()
            self.device_id_hint.config(
                text=t("finish_secondary_hint"),
                fg=theme.WARNING_COLOR,
            )
        else:
            self.node_manager_card.pack(fill=tk.X, pady=(0, 8))
            if self.join_key:
                self.join_key_frame.pack(fill=tk.X, pady=(8, 0))
            else:
                self.join_key_frame.pack_forget()
            self.device_id_hint.config(
                text=t("finish_primary_hint"),
                fg=theme.FG_SECONDARY,
            )

    def refresh_health_status(self) -> None:
        """Servislerin canlı çalışma durumunu arka planda sorgular ve kutuları günceller."""
        if not self.controller or not hasattr(self.controller, "installer_engine"):
            return

        def _worker():
            try:
                health = self.controller.installer_engine.get_system_health()
                if self._is_active and self.winfo_exists():
                    self.after(0, lambda: self._apply_health_ui(health))
            except Exception as e:
                logger.debug(f"Sağlık durumu okunamadı: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def _set_box_state(self, box: tk.Frame, lbl: StyledLabel, text: str, color: str) -> None:
        lbl.config(text=text, fg=color)
        box.config(highlightbackground=color, highlightcolor=color)

    def _apply_health_ui(self, health: dict) -> None:
        """Sorgulanan sağlık verilerini 4 kutulu gösterge paneline uygular."""
        if not self.winfo_exists():
            return

        # 1. Caddy
        if health.get("caddy_running"):
            self._set_box_state(self.caddy_box, self.caddy_status_lbl, t("health_running"), theme.SUCCESS_COLOR)
        else:
            self._set_box_state(self.caddy_box, self.caddy_status_lbl, t("health_stopped"), theme.ERROR_COLOR)

        # 2. Cloudflared
        if health.get("cloudflared_running"):
            self._set_box_state(self.cf_box, self.cf_status_lbl, t("health_running"), theme.SUCCESS_COLOR)
        else:
            self._set_box_state(self.cf_box, self.cf_status_lbl, t("health_stopped"), theme.ERROR_COLOR)

        # 3. Syncthing
        if health.get("syncthing_running"):
            self._set_box_state(self.st_box, self.st_status_lbl, t("health_running"), theme.SUCCESS_COLOR)
        else:
            self._set_box_state(self.st_box, self.st_status_lbl, t("health_stopped"), theme.ERROR_COLOR)

        # 4. Eşleşen ve Bağlı Düğümler
        paired = health.get("paired_devices", 0)
        connected = health.get("connected_devices", 0)
        if paired > 0 and connected > 0:
            self._set_box_state(
                self.nodes_box,
                self.nodes_status_lbl,
                t("health_nodes_connected", connected=connected, total=paired),
                theme.SUCCESS_COLOR,
            )
        elif paired > 0:
            self._set_box_state(
                self.nodes_box,
                self.nodes_status_lbl,
                t("health_nodes_waiting", total=paired),
                theme.WARNING_COLOR,
            )
        else:
            self._set_box_state(
                self.nodes_box,
                self.nodes_status_lbl,
                t("health_nodes_none"),
                theme.CARD_BORDER,
            )
            self.nodes_status_lbl.config(fg=theme.FG_SECONDARY)

    def _schedule_periodic_refresh(self) -> None:
        """Sayfa açıkken her 5 saniyede bir durumu otomatik günceller."""
        if not self._is_active:
            return
        self.refresh_health_status()
        self._auto_refresh_job = self.after(5000, self._schedule_periodic_refresh)

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde verileri yükle ve canlı izlemeyi başlat."""
        self._is_active = True
        if self.controller:
            config = self.controller.build_install_config()
            role = getattr(config, "node_role", "primary")
            role_str = role.value if hasattr(role, "value") else str(role)

            device_id = getattr(config, "local_device_id", "") or ""
            saved = {}
            try:
                from core.config_manager import ConfigManager

                saved = ConfigManager().load()
                if not device_id:
                    device_id = saved.get("local_device_id", "")
                if saved.get("node_role") and not self.controller.get_saved_page_data("sync_settings"):
                    role_str = saved["node_role"]
            except Exception as e:
                logger.warning(f"Kayıtlı konfigürasyondan Device ID okunamadı: {e}")

            if not device_id and hasattr(self.controller, "installer_engine"):
                try:
                    device_id = self.controller.installer_engine.syncthing_service.get_device_id()
                except Exception as e:
                    logger.warning(f"Syncthing servisinden Device ID okunamadı: {e}")

            token = getattr(config, "cloudflare_token", "") or saved.get("cloudflare_token", "")
            port = getattr(config, "caddy_port", 80) or saved.get("caddy_port", 80)
            domain = getattr(config, "public_domain", "") or saved.get("public_domain", "")
            if device_id and token and role_str == "primary":
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
            else:
                self.join_key = ""

            self.set_device_id(device_id)
            self.set_node_role(role_str)
            self._schedule_periodic_refresh()

    def on_leave(self) -> None:
        """Sayfadan çıkılırken otomatik yenileme zamanlayıcısını durdur."""
        self._is_active = False
        if self._auto_refresh_job is not None:
            try:
                self.after_cancel(self._auto_refresh_job)
            except Exception:
                pass
            self._auto_refresh_job = None