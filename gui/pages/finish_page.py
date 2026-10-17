"""
Bitiş ve Canlı Yönetim / Durum Paneli sayfası.

4 kutulu canlı servis sağlık paneli (Caddy, Cloudflared, Syncthing, Senkronizasyon Ağı),
tek tıkla servis başlatma/onarma, Cihaz ID / Küme Katılım Kodu (AHWS1) kopyalama
ve Merkez düğüm için Yedek Bilgisayar Yönetimi içerir.
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
    """5. Adım: Canlı Yönetim ve Durum Paneli (Control Center)."""

    PAGE_NAME = "finish"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.local_device_id = ""
        self.join_key = ""
        self.node_role = "primary"
        self._auto_refresh_job = None
        self._is_active = False

        # ─── Üst Başlık ve Rol Rozeti ───────────────────────────────
        header_frame = tk.Frame(self, bg=theme.BG_COLOR)
        header_frame.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(8, 2))

        title_row = tk.Frame(header_frame, bg=theme.BG_COLOR)
        title_row.pack(fill=tk.X)

        self.role_badge = tk.Label(
            title_row,
            text=t("role_badge_primary"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_TERTIARY,
            padx=10,
            pady=4,
        )
        self.role_badge.pack(side=tk.RIGHT, pady=(2, 0))

        self.header_icon = StyledLabel(
            title_row,
            text="✓ ",
            font=("Segoe UI", 18, "bold"),
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_COLOR,
        )
        self.header_icon.pack(side=tk.LEFT)

        self.header_title = StyledLabel(
            title_row,
            text=t("control_center_title"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        self.header_title.pack(side=tk.LEFT)

        self.header_subtitle = StyledLabel(
            header_frame,
            text=t("finish_success_msg"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=760,
            justify=tk.LEFT,
        )
        self.header_subtitle.pack(anchor=tk.W, pady=(1, 0))

        # ─── İçerik Alanı ───────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=(4, 6))

        # ─── 1. Canlı Sistem ve Servis Durumu Kartı (4 Kutulu Grid) ─
        self.health_card = CardFrame(content, padx=16, pady=8)
        self.health_card.pack(fill=tk.X, pady=(0, 6))

        health_header = tk.Frame(self.health_card, bg=theme.BG_SECONDARY)
        health_header.pack(fill=tk.X, pady=(0, 8))

        self.refresh_btn = SecondaryButton(
            health_header,
            text=t("btn_refresh_status"),
            command=self.refresh_health_status,
            width=15,
            pady=4,
        )
        self.refresh_btn.pack(side=tk.RIGHT)

        self.restart_svc_btn = SecondaryButton(
            health_header,
            text=t("btn_restart_services"),
            command=self._restart_services,
            width=22,
            pady=4,
        )
        self.restart_svc_btn.pack(side=tk.RIGHT, padx=(0, 8))

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
        self.device_id_card = CardFrame(content, padx=16, pady=10)
        self.device_id_card.pack(fill=tk.X, pady=(0, 8))

        device_id_title = StyledLabel(
            self.device_id_card,
            text=t("finish_device_id_title"),
            font=theme.FONT_SMALL_BOLD,
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
            width=16,
            pady=4,
        )
        self.copy_id_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.device_id_label = StyledLabel(
            device_id_row,
            text=t("finish_loading"),
            font=theme.FONT_MONO_SMALL,
            fg=theme.ACCENT_COLOR,
            bg=theme.ENTRY_BG,
            padx=10,
            pady=5,
            anchor=tk.W,
        )
        self.device_id_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Küme Katılım Anahtarı satırı (Sadece Merkez düğümde gösterilir)
        self.join_key_frame = tk.Frame(self.device_id_card, bg=theme.BG_SECONDARY)

        join_title_lbl = StyledLabel(
            self.join_key_frame,
            text=f"{t('finish_join_key_title')} — {t('finish_join_key_desc')}",
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        join_title_lbl.pack(anchor=tk.W, pady=(6, 3))

        join_row = tk.Frame(self.join_key_frame, bg=theme.BG_SECONDARY)
        join_row.pack(fill=tk.X)

        self.copy_join_btn = PrimaryButton(
            join_row,
            text=t("btn_copy_join_key"),
            command=self._copy_join_key,
            width=22,
            pady=4,
        )
        self.copy_join_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.join_key_preview = StyledLabel(
            join_row,
            text="",
            font=theme.FONT_MONO_SMALL,
            fg=theme.SUCCESS_COLOR,
            bg=theme.ENTRY_BG,
            padx=10,
            pady=5,
            anchor=tk.W,
        )
        self.join_key_preview.pack(side=tk.LEFT, fill=tk.X, expand=True)

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

        # ─── 3. Hızlı İşlemler ve Küme Yönetimi Kartı ───────────────
        self.actions_card = CardFrame(content, padx=16, pady=10, border_color=theme.ACCENT_COLOR)
        self.actions_card.pack(fill=tk.X, pady=(0, 8))
        self.node_manager_card = self.actions_card

        open_site_desc = StyledLabel(
            self.actions_card,
            text=t("finish_open_site_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=740,
            justify=tk.LEFT,
        )
        open_site_desc.pack(anchor=tk.W, pady=(0, 8))

        # Merkez düğüm için 2x2 dengeli buton grid'i
        self.primary_actions_grid = tk.Frame(self.actions_card, bg=theme.BG_SECONDARY)
        self.primary_actions_grid.grid_columnconfigure(0, weight=1, uniform="p_act")
        self.primary_actions_grid.grid_columnconfigure(1, weight=1, uniform="p_act")

        self.open_site_btn = PrimaryButton(
            self.primary_actions_grid,
            text=t("btn_open_site_browser"),
            command=self._open_website,
        )
        self.open_site_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 6))

        self.add_node_btn = PrimaryButton(
            self.primary_actions_grid,
            text=t("btn_add_node"),
            command=self._open_node_manager,
        )
        self.add_node_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=(0, 6))

        self.open_st_btn = SecondaryButton(
            self.primary_actions_grid,
            text=t("btn_open_syncthing"),
            command=self._open_syncthing_ui,
        )
        self.open_st_btn.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self.settings_btn = SecondaryButton(
            self.primary_actions_grid,
            text=t("btn_settings"),
            command=self._open_settings,
        )
        self.settings_btn.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Yedek düğüm için 1x3 dengeli buton grid'i
        self.secondary_actions_grid = tk.Frame(self.actions_card, bg=theme.BG_SECONDARY)
        for col in range(3):
            self.secondary_actions_grid.grid_columnconfigure(col, weight=1, uniform="s_act")

        PrimaryButton(
            self.secondary_actions_grid,
            text=t("btn_open_site_browser"),
            command=self._open_website,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        SecondaryButton(
            self.secondary_actions_grid,
            text=t("btn_open_syncthing"),
            command=self._open_syncthing_ui,
        ).grid(row=0, column=1, sticky="ew", padx=6)

        SecondaryButton(
            self.secondary_actions_grid,
            text=t("btn_settings"),
            command=self._open_settings,
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        # ─── Alt Butonlar (Kurulum Sihirbazı & Kapat) ───────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 4))

        home_btn = SecondaryButton(
            footer,
            text=t("btn_reinstall_wizard"),
            command=self._go_home,
            width=18,
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
            padx=10,
            pady=7,
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
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_SECONDARY,
            bg=theme.ENTRY_BG,
        )
        status_lbl.pack(anchor=tk.W, pady=(2, 0))
        return box, status_lbl

    def _restart_services(self) -> None:
        """Tüm AHWS servislerini arka planda yeniden başlatır ve durumu günceller."""
        if not self.controller or not hasattr(self.controller, "installer_engine"):
            return

        self.restart_svc_btn.set_state("disabled")
        self.restart_svc_btn.config(text=t("msg_restarting_services"))

        def _worker():
            try:
                health = self.controller.installer_engine.restart_all_services()
                if self.winfo_exists():
                    self.after(0, lambda: self._on_restart_done(health))
            except Exception as e:
                logger.warning(f"Servisler yeniden başlatılırken hata: {e}")
                if self.winfo_exists():
                    self.after(0, lambda: self._on_restart_done(None))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_restart_done(self, health: dict | None) -> None:
        if not self.winfo_exists():
            return
        self.restart_svc_btn.set_state("normal")
        self.restart_svc_btn.config(text=t("btn_restart_services"))
        if health:
            self._apply_health_ui(health)
        else:
            self.refresh_health_status()

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

    def _flash_button_copied(self, btn, original_key: str) -> None:
        """Kopyala butonunda 2 saniyeliğine yeşil '✓ Kopyalandı' geri bildirimi gösterir."""
        btn.config(text=t("btn_copied_inline"))
        self.after(
            2000,
            lambda: btn.config(text=t(original_key)) if btn.winfo_exists() else None,
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
        """Hoşgeldiniz / Kurulum sihirbazı ekranına döner."""
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
        """Node rolünü ayarlar. 'secondary' ise Yedek Ekle butonunu ve Join Key'i gizler."""
        self.node_role = role
        if role == "secondary":
            self.role_badge.config(text=f"● {t('role_badge_secondary')}", fg=theme.WARNING_COLOR)
            self.join_key_frame.pack_forget()
            self.primary_actions_grid.pack_forget()
            self.secondary_actions_grid.pack(fill=tk.X)
            self.device_id_hint.config(
                text=t("finish_secondary_hint"),
                fg=theme.WARNING_COLOR,
            )
        else:
            self.role_badge.config(text=f"● {t('role_badge_primary')}", fg=theme.ACCENT_COLOR)
            self.secondary_actions_grid.pack_forget()
            self.primary_actions_grid.pack(fill=tk.X)
            if self.join_key:
                preview = self.join_key if len(self.join_key) <= 58 else f"{self.join_key[:55]}..."
                self.join_key_preview.config(text=preview)
                self.join_key_frame.pack(fill=tk.X, before=self.device_id_hint)
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
        port = health.get("caddy_port", 80)
        if health.get("caddy_running"):
            self._set_box_state(
                self.caddy_box,
                self.caddy_status_lbl,
                f"{t('health_running')} (:{port})",
                theme.SUCCESS_COLOR,
            )
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
            # Eğer kurulumdan hemen sonra gelindiyse başlığı "Kurulum Tamamlandı!",
            # doğrudan kontrol paneli olarak açıldıysa "AHWS Canlı Yönetim ve Durum Paneli" yap
            just_installed = len(getattr(self.controller, "_page_stack", [])) > 1
            if just_installed:
                self.header_title.config(text=t("finish_title"), fg=theme.SUCCESS_COLOR)
            else:
                self.header_title.config(text=t("control_center_title"), fg=theme.FG_COLOR)

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

            token = saved.get("cloudflare_token", "") or getattr(config, "cloudflare_token", "")
            port = saved.get("caddy_port", 0) or getattr(config, "caddy_port", 80)
            domain = saved.get("public_domain", "") or getattr(config, "public_domain", "")
            site_root = saved.get("site_root_path", "") or getattr(config, "site_root_path", "")

            # Alt başlıkta aktif klasör ve domain özetini göster
            summary_parts = [t("finish_success_msg")]
            if site_root:
                summary_parts.append(f"Klasör: {site_root}")
            if domain:
                summary_parts.append(f"Domain: {domain}")
            self.header_subtitle.config(text="   |   ".join(summary_parts))

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