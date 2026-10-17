"""
Ayarlar Diyaloğu.

Kurulum tamamlandıktan sonra, mevcut Cloudflare token, Caddy port,
Domain ve Web Sitesi Klasörü gibi ayarları değiştirmek için kullanılır.
"""

import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from gui import theme
from gui.widgets import (
    CardFrame,
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


class SettingsDialog(tk.Toplevel):
    """
    Kurulum sonrası ayarların değiştirilebildiği pencere.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.title(t("settings_title"))
        self.geometry("640x700")
        self.resizable(False, False)
        self.configure(bg=theme.BG_COLOR)
        self.transient(parent)
        self.grab_set()

        # Pencereyi merkeze konumlandır
        self._center_window()

        self._load_current_settings()
        self._build_ui()

    def _load_current_settings(self):
        """Mevcut ayarları yükler."""
        self.current_settings = {}
        try:
            from core.config_manager import ConfigManager
            self.config_mgr = ConfigManager()
            self.current_settings = self.config_mgr.load()
        except Exception as e:
            logger.error(f"Ayarlar yüklenemedi: {e}")

    def _build_ui(self):
        """Arayüzü oluşturur."""
        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=theme.PADDING_LARGE)
        content.pack(fill=tk.BOTH, expand=True)

        title_label = StyledLabel(
            content,
            text=t("settings_header"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        desc_label = StyledLabel(
            content,
            text=t("settings_desc"),
            font=theme.FONT_SMALL,
            fg=theme.WARNING_COLOR,
            bg=theme.BG_COLOR,
            wraplength=580,
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

        # ─── Web Sitesi Klasörü ───
        folder_card = CardFrame(content)
        folder_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        folder_title = StyledLabel(folder_card, text=t("server_folder_title"), font=theme.FONT_MEDIUM, fg=theme.FG_COLOR, bg=theme.BG_SECONDARY)
        folder_title.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        folder_row = tk.Frame(folder_card, bg=theme.BG_SECONDARY)
        folder_row.pack(fill=tk.X)

        self.folder_var = tk.StringVar(value=self.current_settings.get("site_root_path", ""))
        self.folder_entry = StyledEntry(folder_row, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, theme.PADDING_SMALL))

        browse_btn = SecondaryButton(folder_row, text=t("btn_browse"), command=self._browse_folder, width=14)
        browse_btn.pack(side=tk.RIGHT)

        # ─── Cloudflare Tunnel Token ───
        token_card = CardFrame(content)
        token_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        token_title = StyledLabel(token_card, text=t("server_token_title"), font=theme.FONT_MEDIUM, fg=theme.FG_COLOR, bg=theme.BG_SECONDARY)
        token_title.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.token_var = tk.StringVar(value=self.current_settings.get("cloudflare_token", ""))
        self.token_entry = StyledEntry(token_card, textvariable=self.token_var, width=60, show="•")
        self.token_entry.pack(fill=tk.X)

        # ─── Public Domain ───
        domain_card = CardFrame(content)
        domain_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        domain_title = StyledLabel(domain_card, text=t("server_domain_title"), font=theme.FONT_MEDIUM, fg=theme.FG_COLOR, bg=theme.BG_SECONDARY)
        domain_title.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.domain_var = tk.StringVar(value=self.current_settings.get("public_domain", ""))
        self.domain_entry = StyledEntry(domain_card, textvariable=self.domain_var, width=60)
        self.domain_entry.pack(fill=tk.X)

        # ─── Caddy Portu ───
        port_card = CardFrame(content)
        port_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        port_title = StyledLabel(port_card, text=t("server_port_title"), font=theme.FONT_MEDIUM, fg=theme.FG_COLOR, bg=theme.BG_SECONDARY)
        port_title.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        port_row = tk.Frame(port_card, bg=theme.BG_SECONDARY)
        port_row.pack(anchor=tk.W)

        self.port_var = tk.StringVar(value=str(self.current_settings.get("caddy_port", constants.CADDY_DEFAULT_PORT)))
        self.port_spinbox = tk.Spinbox(
            port_row, from_=1, to=65535, textvariable=self.port_var, width=10,
            font=theme.FONT_NORMAL, bg=theme.ENTRY_BG, fg=theme.ENTRY_FG,
            insertbackground=theme.FG_COLOR, relief=tk.FLAT,
            highlightthickness=theme.BORDER_WIDTH, highlightbackground=theme.ENTRY_BORDER,
            highlightcolor=theme.ACCENT_COLOR, buttonbackground=theme.BUTTON_BG,
        )
        self.port_spinbox.pack(side=tk.LEFT)

        self.port_status_label = StyledLabel(port_row, text="", font=theme.FONT_SMALL, fg=theme.SUCCESS_COLOR, bg=theme.BG_SECONDARY)
        self.port_status_label.pack(side=tk.LEFT, padx=(theme.PADDING_MEDIUM, 0))
        self.port_var.trace_add("write", self._on_port_change)
        self._update_port_status()

        # ─── Durum / Bilgi ───
        self.status_label = StyledLabel(content, text="", font=theme.FONT_SMALL, fg=theme.SUCCESS_COLOR, bg=theme.BG_COLOR)
        self.status_label.pack(pady=theme.PADDING_SMALL)

        # ─── Alt Butonlar ───
        btn_frame = tk.Frame(content, bg=theme.BG_COLOR)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 0))

        cancel_btn = SecondaryButton(btn_frame, text=t("btn_cancel"), command=self.destroy, width=12)
        cancel_btn.pack(side=tk.LEFT)

        uninstall_btn = SecondaryButton(
            btn_frame,
            text=t("btn_uninstall"),
            command=self._on_uninstall,
            width=18,
        )
        uninstall_btn.pack(side=tk.LEFT, padx=(theme.PADDING_SMALL, 0))

        save_btn = PrimaryButton(btn_frame, text=t("btn_save"), command=self._on_save, width=16)
        save_btn.pack(side=tk.RIGHT)

    def _browse_folder(self) -> None:
        initial_dir = self.folder_var.get() or str(Path.home())
        selected = filedialog.askdirectory(parent=self, title=t("btn_browse"), initialdir=initial_dir)
        if selected:
            self.folder_var.set(selected)

    def _on_port_change(self, *_args) -> None:
        self._update_port_status()

    def _update_port_status(self) -> None:
        try:
            port = int(self.port_var.get() or "0")
            if 1 <= port <= 65535:
                if is_port_available(port) or is_port_in_use_by_caddy(port):
                    self.port_status_label.config(text=t("server_port_ok"), fg=theme.SUCCESS_COLOR)
                else:
                    self.port_status_label.config(text=t("server_port_in_use"), fg=theme.ERROR_COLOR)
            else:
                self.port_status_label.config(text=t("server_port_invalid"), fg=theme.ERROR_COLOR)
        except ValueError:
            self.port_status_label.config(text=t("server_port_invalid"), fg=theme.ERROR_COLOR)

    def _center_window(self) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 640) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")

    def _validate(self) -> bool:
        role = self.current_settings.get("node_role", "primary")

        # Klasör
        folder_path = self.folder_var.get().strip()
        if not folder_path:
            messagebox.showerror(t("settings_error_title"), t("err_no_folder"), parent=self)
            return False

        if role == "secondary":
            try:
                Path(folder_path).mkdir(parents=True, exist_ok=True)
            except Exception:
                messagebox.showerror(t("settings_error_title"), t("err_folder_not_found", folder=folder_path), parent=self)
                return False
        else:
            if not os.path.isdir(folder_path):
                messagebox.showerror(t("settings_error_title"), t("err_folder_not_found", folder=folder_path), parent=self)
                return False

            index_path = Path(folder_path) / "index.html"
            if not index_path.is_file():
                messagebox.showerror(t("settings_error_title"), t("err_no_index", index_path=index_path), parent=self)
                return False

        # Token
        token = self.token_var.get().strip()
        if not token or not re.match(constants.CLOUDFLARE_TOKEN_REGEX, token):
            messagebox.showerror(t("settings_error_title"), t("err_invalid_token"), parent=self)
            return False

        # Port
        try:
            port = int(self.port_var.get() or "0")
            if not (1 <= port <= 65535):
                messagebox.showerror(t("settings_error_title"), t("err_port_range"), parent=self)
                return False
            if not is_port_available(port) and not is_port_in_use_by_caddy(port):
                messagebox.showerror(t("settings_error_title"), t("err_port_in_use_msg", port=port), parent=self)
                return False
        except ValueError:
            messagebox.showerror(t("settings_error_title"), t("server_port_invalid"), parent=self)
            return False

        return True

    def _on_save(self) -> None:
        if not self._validate():
            return

        new_folder = self.folder_var.get().strip()
        new_token = self.token_var.get().strip()
        new_domain = self.domain_var.get().strip()
        new_port = int(self.port_var.get().strip())

        folder_changed = new_folder != self.current_settings.get("site_root_path")
        token_changed = new_token != self.current_settings.get("cloudflare_token")
        domain_changed = new_domain != self.current_settings.get("public_domain")
        port_changed = new_port != self.current_settings.get("caddy_port")

        if not (folder_changed or token_changed or domain_changed or port_changed):
            self.destroy()
            return

        self.status_label.config(text=t("settings_applying"), fg=theme.INFO_COLOR)
        self.update_idletasks()

        try:
            # 1. Konfigürasyonu Güncelle
            self.current_settings["site_root_path"] = new_folder
            self.current_settings["cloudflare_token"] = new_token
            self.current_settings["public_domain"] = new_domain
            self.current_settings["caddy_port"] = new_port
            self.config_mgr.save(self.current_settings)

            engine = getattr(self.controller, "installer_engine", None)
            if engine:
                # 2. Caddy ve Syncthing Klasör Güncelle
                if folder_changed or port_changed:
                    engine.caddy_service.generate_caddyfile(new_folder, new_port)
                    engine.caddy_service.restart()

                if folder_changed:
                    engine.syncthing_service.update_folder_path("auto-home-web", new_folder)

                # 3. Cloudflared Güncelle
                if token_changed:
                    engine.cloudflare_service.install(new_token)

            messagebox.showinfo(t("settings_saved_title"), t("settings_saved_msg"), parent=self)
            self.destroy()
        except Exception as e:
            logger.error(f"Ayarlar kaydedilirken hata: {e}")
            messagebox.showerror(t("settings_error_title"), t("settings_error_msg", error=e), parent=self)
            self.status_label.config(text=t("settings_save_failed"), fg=theme.ERROR_COLOR)

    def _on_uninstall(self) -> None:
        """Kurulumu tamamen kaldırır."""
        confirmed = messagebox.askyesno(
            t("uninstall_confirm_title"),
            t("uninstall_confirm_msg"),
            parent=self,
        )
        if not confirmed:
            return

        self.status_label.config(text=t("settings_applying"), fg=theme.WARNING_COLOR)
        self.update_idletasks()

        try:
            engine = getattr(self.controller, "installer_engine", None)
            if engine:
                engine.uninstall_all()
            elif hasattr(self, "config_mgr"):
                self.config_mgr.delete()

            messagebox.showinfo(
                t("uninstall_success_title"),
                t("uninstall_success_msg"),
                parent=self,
            )
            self.destroy()
            if self.controller:
                self.controller.go_to_page("welcome")
        except Exception as e:
            logger.error(f"Kaldırma işlemi sırasında hata: {e}")
            messagebox.showerror(t("settings_error_title"), str(e), parent=self)
