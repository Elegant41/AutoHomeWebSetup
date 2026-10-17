"""
Hoşgeldiniz sayfası.

Logo, 3'lü mimari özellik kartları, mevcut kurulum algılama ve İleri / Yönetim butonlarını içerir.
"""

import tkinter as tk

from gui import theme
from gui.base_page import BasePage
from gui.widgets import CardFrame, PrimaryButton, SecondaryButton, StyledLabel
from utils.i18n import t
from utils.logger import get_logger
from utils.resource_path import resource_path

logger = get_logger(__name__)


class WelcomePage(BasePage):
    """1. Adım: Hoşgeldiniz ekranı (Mevcut kurulum ve düğüm yönetimi destekli)."""

    PAGE_NAME = "welcome"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # ─── Üst Hero / Logo Alanı ──────────────────────────────────
        hero_frame = tk.Frame(self, bg=theme.BG_COLOR)
        hero_frame.pack(fill=tk.X, pady=(18, 8))

        try:
            self._logo_img = tk.PhotoImage(file=str(resource_path("assets/logo.png")))
            tk.Label(hero_frame, image=self._logo_img, bg=theme.BG_COLOR, bd=0).pack(pady=(0, 6))
        except Exception as exc:
            logger.warning(f"Logo yüklenemedi: {exc}")

        title_label = StyledLabel(
            hero_frame,
            text=t("welcome_title"),
            font=("Segoe UI", 26, "bold"),
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(pady=(2, 2))

        subtitle_label = StyledLabel(
            hero_frame,
            text=t("welcome_subtitle"),
            font=theme.FONT_NORMAL,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_COLOR,
        )
        subtitle_label.pack(pady=(0, 6))

        # ─── 1. Standart Açıklama & 3'lü Özellik Kartları (Sıfır Kurulum) ─
        self.normal_info_card = tk.Frame(self, bg=theme.BG_COLOR)
        self.normal_info_card.pack(fill=tk.X, padx=40, pady=6)

        desc_card = CardFrame(self.normal_info_card, padx=20, pady=14)
        desc_card.pack(fill=tk.X, pady=(0, 12))

        info_label = StyledLabel(
            desc_card,
            text=t("welcome_desc"),
            font=theme.FONT_NORMAL,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
            justify=tk.LEFT,
            wraplength=720,
        )
        info_label.pack(anchor=tk.W)

        # 3'lü Mimari Özellik Grid'i
        feat_grid = tk.Frame(self.normal_info_card, bg=theme.BG_COLOR)
        feat_grid.pack(fill=tk.X)
        for col in range(3):
            feat_grid.grid_columnconfigure(col, weight=1, uniform="feat_col")

        self._create_feature_box(
            feat_grid, 0, t("feat_1_title"), t("feat_1_desc"), theme.ACCENT_COLOR
        )
        self._create_feature_box(
            feat_grid, 1, t("feat_2_title"), t("feat_2_desc"), theme.INFO_COLOR
        )
        self._create_feature_box(
            feat_grid, 2, t("feat_3_title"), t("feat_3_desc"), theme.SUCCESS_COLOR
        )

        # ─── 2. Mevcut Kurulum Algılandı Kartı ───────────────────────
        self.existing_frame = CardFrame(
            self,
            padx=26,
            pady=18,
            border_color=theme.SUCCESS_COLOR,
        )

        existing_title = StyledLabel(
            self.existing_frame,
            text=t("welcome_existing_title"),
            font=theme.FONT_LARGE,
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
            wraplength=700,
        )
        self.existing_info_label.pack(anchor=tk.W, pady=(0, 14))

        existing_btn_row1 = tk.Frame(self.existing_frame, bg=theme.BG_SECONDARY)
        existing_btn_row1.pack(fill=tk.X, pady=(0, 8))

        self.open_site_btn = PrimaryButton(
            existing_btn_row1,
            text=t("btn_open_site"),
            command=self._open_website,
            width=28,
        )
        self.open_site_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.settings_btn = SecondaryButton(
            existing_btn_row1,
            text=t("btn_settings"),
            command=self._open_settings,
            width=28,
        )
        self.settings_btn.pack(side=tk.LEFT)

        existing_btn_row2 = tk.Frame(self.existing_frame, bg=theme.BG_SECONDARY)
        existing_btn_row2.pack(fill=tk.X)

        self.manage_btn = PrimaryButton(
            existing_btn_row2,
            text=t("btn_go_to_manage"),
            command=self._go_to_management,
            width=28,
        )
        self.manage_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.reinstall_btn = SecondaryButton(
            existing_btn_row2,
            text=t("btn_reinstall"),
            command=self.next_page,
            width=28,
        )
        self.reinstall_btn.pack(side=tk.LEFT)

        # ─── Alt Alan: UAC Uyarısı & İleri Butonu ───────────────────
        bottom_frame = tk.Frame(self, bg=theme.BG_COLOR)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=40, pady=(8, 20))

        self.uac_label = StyledLabel(
            bottom_frame,
            text=t("welcome_warning"),
            font=theme.FONT_SMALL,
            fg=theme.WARNING_COLOR,
            bg=theme.BG_COLOR,
            wraplength=720,
            justify=tk.CENTER,
        )
        self.uac_label.pack(pady=(0, 12))

        self.next_btn = PrimaryButton(
            bottom_frame,
            text=t("btn_next"),
            command=self.next_page,
            width=20,
            pady=8,
        )
        self.next_btn.pack()

    def _create_feature_box(
        self, parent: tk.Frame, col: int, title_text: str, desc_text: str, accent: str
    ) -> None:
        pad_left = 0 if col == 0 else 6
        pad_right = 0 if col == 2 else 6

        box = CardFrame(parent, padx=14, pady=12)
        box.grid(row=0, column=col, sticky="nsew", padx=(pad_left, pad_right))

        t_lbl = StyledLabel(
            box,
            text=title_text,
            font=theme.FONT_NORMAL_BOLD,
            fg=accent,
            bg=theme.BG_SECONDARY,
        )
        t_lbl.pack(anchor=tk.W, pady=(0, 4))

        d_lbl = StyledLabel(
            box,
            text=desc_text,
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
            wraplength=220,
            justify=tk.LEFT,
        )
        d_lbl.pack(anchor=tk.W)

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
                self.existing_frame.pack(fill=tk.X, padx=40, pady=8)
            else:
                self.existing_frame.pack_forget()
                self.normal_info_card.pack(fill=tk.X, padx=40, pady=6)
                self.next_btn.pack()
        except Exception as e:
            logger.warning(f"Mevcut kurulum kontrolü sırasında hata: {e}")