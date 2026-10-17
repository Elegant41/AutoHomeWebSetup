"""
Hoşgeldiniz sayfası.

Logo, açıklama metni, dil seçimi, mevcut kurulum algılama ve İleri / Yönetim butonu içerir.
"""

import tkinter as tk

from gui import theme
from gui.base_page import BasePage
from gui.widgets import PrimaryButton, SecondaryButton, StyledLabel
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


class WelcomePage(BasePage):
    """1. Adım: Hoşgeldiniz ekranı (Mevcut kurulum ve düğüm yönetimi destekli)."""

    PAGE_NAME = "welcome"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # ─── Dil Seçimi ─────────────────────────────────────────────
        lang_frame = tk.Frame(self, bg=theme.BG_COLOR)
        lang_frame.pack(fill=tk.X, anchor=tk.E, padx=20, pady=10)

        btn_tr = SecondaryButton(
            lang_frame,
            text="TR",
            command=lambda: self.controller.change_language("tr"),
            width=6,
        )
        btn_tr.pack(side=tk.RIGHT, padx=5)

        btn_en = SecondaryButton(
            lang_frame,
            text="EN",
            command=lambda: self.controller.change_language("en"),
            width=6,
        )
        btn_en.pack(side=tk.RIGHT, padx=5)

        # ─── Üst Boşluk ─────────────────────────────────────────────
        tk.Frame(self, bg=theme.BG_COLOR, height=10).pack(fill=tk.X)

        # ─── Başlık ─────────────────────────────────────────────────
        title_label = StyledLabel(
            self,
            text=t("welcome_title"),
            font=("Segoe UI", 32, "bold"),
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(pady=(10, 4))

        subtitle_label = StyledLabel(
            self,
            text=t("welcome_subtitle"),
            font=theme.FONT_LARGE,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
        )
        subtitle_label.pack(pady=(0, 16))

        # ─── 1. Standart Açıklama Kartı (Sıfır Kurulum) ────────────
        self.normal_info_card = tk.Frame(self, bg=theme.BG_SECONDARY, padx=30, pady=20)
        self.normal_info_card.pack(fill=tk.X, padx=60, pady=10)

        info_label = StyledLabel(
            self.normal_info_card,
            text=t("welcome_desc"),
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            justify=tk.LEFT,
            wraplength=580,
        )
        info_label.pack(anchor=tk.W)

        # ─── 2. Mevcut Kurulum Algılandı Kartı ───────────────────────
        self.existing_frame = tk.Frame(self, bg=theme.BG_SECONDARY, padx=30, pady=20)

        existing_title = StyledLabel(
            self.existing_frame,
            text=t("welcome_existing_title"),
            font=theme.FONT_TITLE,
            fg=theme.SUCCESS_COLOR,
            bg=theme.BG_SECONDARY,
        )
        existing_title.pack(anchor=tk.W, pady=(0, 6))

        self.existing_info_label = StyledLabel(
            self.existing_frame,
            text="",
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            justify=tk.LEFT,
            wraplength=580,
        )
        self.existing_info_label.pack(anchor=tk.W, pady=(0, 16))

        existing_btn_row1 = tk.Frame(self.existing_frame, bg=theme.BG_SECONDARY)
        existing_btn_row1.pack(fill=tk.X, pady=(0, 10))

        self.open_site_btn = PrimaryButton(
            existing_btn_row1,
            text=t("btn_open_site"),
            command=self._open_website,
            width=26,
        )
        self.open_site_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.settings_btn = SecondaryButton(
            existing_btn_row1,
            text=t("btn_settings"),
            command=self._open_settings,
            width=26,
        )
        self.settings_btn.pack(side=tk.LEFT)

        existing_btn_row2 = tk.Frame(self.existing_frame, bg=theme.BG_SECONDARY)
        existing_btn_row2.pack(fill=tk.X)

        self.manage_btn = SecondaryButton(
            existing_btn_row2,
            text=t("btn_go_to_manage"),
            command=self._go_to_management,
            width=26,
        )
        self.manage_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.reinstall_btn = SecondaryButton(
            existing_btn_row2,
            text=t("btn_reinstall"),
            command=self.next_page,
            width=26,
        )
        self.reinstall_btn.pack(side=tk.LEFT)

        # ─── UAC Uyarısı ────────────────────────────────────────────
        self.uac_label = StyledLabel(
            self,
            text=t("welcome_warning"),
            font=theme.FONT_SMALL,
            fg=theme.WARNING_COLOR,
            bg=theme.BG_COLOR,
            wraplength=580,
            justify=tk.CENTER,
        )
        self.uac_label.pack(pady=(12, 16))

        # ─── İleri Butonu (Sadece sıfır kurulumda gösterilir) ───────
        self.next_btn = PrimaryButton(
            self,
            text=t("btn_next"),
            command=self.next_page,
            width=16,
        )
        self.next_btn.pack(pady=10)

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

    def _go_to_management(self) -> None:
        """Doğrudan bitiş / canlı durum yönetimi sayfasına geçer."""
        if self.controller:
            self.controller.go_to_page("finish")

    def on_enter(self) -> None:
        """Sayfa gösterildiğinde mevcut kurulum kontrolü yap."""
        try:
            from core.config_manager import ConfigManager

            config_mgr = ConfigManager()
            if config_mgr.exists():
                data = config_mgr.load()
                role = data.get("node_role", "primary")
                role_txt = t("sync_role_primary") if role == "primary" else t("sync_role_secondary")
                dev_id = data.get("local_device_id", "")
                if not dev_id and hasattr(self.controller, "installer_engine"):
                    try:
                        dev_id = self.controller.installer_engine.syncthing_service.get_device_id()
                    except Exception:
                        pass

                raw_date = data.get("install_date", "")
                if raw_date and "T" in raw_date:
                    date_str = raw_date.replace("T", " ")[:19]
                else:
                    date_str = raw_date or t("welcome_unknown_date")

                dev_id_str = f"\n• {t('welcome_device_id_label')}: {dev_id}" if dev_id else ""
                desc_text = (
                    f"{t('welcome_existing_desc')}\n\n"
                    f"• {t('finish_role')}: {role_txt}\n"
                    f"• {t('install_date_label')}: {date_str}{dev_id_str}"
                )
                self.existing_info_label.config(text=desc_text)

                if role == "secondary":
                    self.manage_btn.config(text=t("btn_go_to_status"))
                else:
                    self.manage_btn.config(text=t("btn_go_to_manage"))

                self.normal_info_card.pack_forget()
                self.next_btn.pack_forget()
                self.existing_frame.pack(fill=tk.X, padx=60, pady=10, before=self.uac_label)
            else:
                self.existing_frame.pack_forget()
                self.normal_info_card.pack(fill=tk.X, padx=60, pady=10, before=self.uac_label)
                self.next_btn.pack(pady=10)
        except Exception as e:
            logger.warning(f"Mevcut kurulum kontrolü sırasında hata: {e}")