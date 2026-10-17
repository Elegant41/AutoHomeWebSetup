"""
Yedek Node Yönetimi Diyaloğu.

Merkez bilgisayarda, kurulum tamamlandıktan sonra yeni bir yedek düğümü
(bilgisayarı) Syncthing ağına eklemek, mevcut eşleşmiş yedek düğümlerin
canlı bağlantı durumunu görmek veya kaldırmak için kullanılır.
"""

import re
import threading
import tkinter as tk
from tkinter import messagebox

from gui import theme
from gui.widgets import (
    CardFrame,
    DangerButton,
    PrimaryButton,
    SecondaryButton,
    StyledEntry,
    StyledLabel,
)
from utils import constants
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


class NodeManagerDialog(tk.Toplevel):
    """
    Yedek node ekleme ve yönetim diyaloğu.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.title(t("node_dialog_title"))
        self.geometry("700x580")
        self.resizable(False, False)
        self.configure(bg=theme.BG_COLOR)
        self.transient(parent)

        try:
            from utils.resource_path import resource_path

            icon_path = resource_path("assets/icon.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        theme.apply_dark_titlebar(self)

        try:
            self.grab_set()
        except Exception:
            pass

        self._center_window()

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=18)
        content.pack(fill=tk.BOTH, expand=True)

        title_label = StyledLabel(
            content,
            text=t("node_dialog_title"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(anchor=tk.W, pady=(0, 2))

        desc_label = StyledLabel(
            content,
            text=t("node_dialog_desc"),
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=640,
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, pady=(0, 10))

        # ─── 1. Ana Bilgisayar Cihaz ID & Katılım Kodu Kartı ────────
        self.local_device_id = ""
        self.join_key = ""
        try:
            from core.config_manager import ConfigManager
            from core.models import InstallConfig

            saved = ConfigManager().load()
            self.local_device_id = saved.get("local_device_id", "")
            token = saved.get("cloudflare_token", "")
            port = saved.get("caddy_port", 80)
            domain = saved.get("public_domain", "")
            if self.local_device_id and token:
                self.join_key = InstallConfig.generate_join_key(
                    primary_device_id=self.local_device_id,
                    cloudflare_token=token,
                    caddy_port=int(port),
                    public_domain=domain,
                )
        except Exception:
            pass

        if not self.local_device_id and self.controller and hasattr(self.controller, "installer_engine"):
            try:
                self.local_device_id = self.controller.installer_engine.syncthing_service.get_device_id()
            except Exception:
                pass

        if self.local_device_id:
            local_card = CardFrame(content, padx=14, pady=10)
            local_card.pack(fill=tk.X, pady=(0, 10))

            local_header = tk.Frame(local_card, bg=theme.BG_SECONDARY)
            local_header.pack(fill=tk.X, pady=(0, 6))

            if self.join_key:
                self.copy_join_btn = PrimaryButton(
                    local_header,
                    text=t("btn_copy_join_key"),
                    command=self._copy_join_key,
                    width=20,
                    pady=3,
                    font=theme.FONT_SMALL_BOLD,
                )
                self.copy_join_btn.pack(side=tk.RIGHT, padx=(6, 0))

            local_title = StyledLabel(
                local_header,
                text=t("node_dialog_local_id_title"),
                font=theme.FONT_SMALL_BOLD,
                fg=theme.FG_SECONDARY,
                bg=theme.BG_SECONDARY,
            )
            local_title.pack(side=tk.LEFT)

            local_row = tk.Frame(local_card, bg=theme.BG_SECONDARY)
            local_row.pack(fill=tk.X)

            self.copy_local_btn = SecondaryButton(
                local_row,
                text=t("btn_copy"),
                command=self._copy_local_id,
                width=12,
                pady=4,
            )
            self.copy_local_btn.pack(side=tk.RIGHT, padx=(6, 0))

            local_id_lbl = StyledLabel(
                local_row,
                text=self.local_device_id,
                font=theme.FONT_MONO_SMALL,
                fg=theme.ACCENT_COLOR,
                bg=theme.ENTRY_BG,
                padx=8,
                pady=5,
                anchor=tk.W,
            )
            local_id_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── 2. Yeni Yedek Device ID Ekleme Kartı ───────────────────
        device_card = CardFrame(content, padx=14, pady=10, border_color=theme.ACCENT_COLOR)
        device_card.pack(fill=tk.X, pady=(0, 10))

        device_label = StyledLabel(
            device_card,
            text=t("node_dialog_input_title"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_label.pack(anchor=tk.W, pady=(0, 6))

        input_row = tk.Frame(device_card, bg=theme.BG_SECONDARY)
        input_row.pack(fill=tk.X)

        self.add_btn = PrimaryButton(
            input_row,
            text=t("node_dialog_btn_add"),
            command=self._on_add_clicked,
            width=16,
            pady=4,
        )
        self.add_btn.pack(side=tk.RIGHT, padx=(6, 0))

        paste_btn = SecondaryButton(
            input_row,
            text=t("btn_paste"),
            command=self._paste_device_id,
            width=9,
            pady=4,
        )
        paste_btn.pack(side=tk.RIGHT, padx=(6, 0))

        self.device_id_var = tk.StringVar()
        self.device_id_entry = StyledEntry(
            input_row,
            textvariable=self.device_id_var,
            font=theme.FONT_MONO_SMALL,
            width=42,
        )
        self.device_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

        self.device_id_hint = StyledLabel(
            device_card,
            text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
            font=theme.FONT_SMALL,
            fg=theme.FG_DISABLED,
            bg=theme.BG_SECONDARY,
            wraplength=600,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(4, 0))
        self.device_id_var.trace_add("write", self._on_device_id_change)

        # ─── 3. Eşleşmiş Yedek Düğümler Listesi Kartı ───────────────
        self.nodes_card = CardFrame(content, padx=14, pady=10)
        self.nodes_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        nodes_header = tk.Frame(self.nodes_card, bg=theme.BG_SECONDARY)
        nodes_header.pack(fill=tk.X, pady=(0, 6))

        nodes_title = StyledLabel(
            nodes_header,
            text=t("node_dialog_paired_title"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        nodes_title.pack(side=tk.LEFT)

        self.nodes_list_frame = tk.Frame(self.nodes_card, bg=theme.BG_SECONDARY)
        self.nodes_list_frame.pack(fill=tk.BOTH, expand=True)

        # ─── Durum & Alt Kapat Butonu ───────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = StyledLabel(
            footer,
            text="",
            font=theme.FONT_SMALL_BOLD,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=480,
            justify=tk.LEFT,
        )
        self.status_label.pack(side=tk.LEFT)

        close_btn = SecondaryButton(
            footer,
            text=t("btn_close"),
            command=self.destroy,
            width=14,
        )
        close_btn.pack(side=tk.RIGHT)

        self._refresh_paired_nodes()

    def _copy_local_id(self) -> None:
        """Ana bilgisayarın Device ID'sini panoya kopyalar."""
        if self.local_device_id:
            self.clipboard_clear()
            self.clipboard_append(self.local_device_id)
            if hasattr(self, "copy_local_btn"):
                self.copy_local_btn.config(text=t("btn_copied_inline"), fg=theme.SUCCESS_COLOR)
                self.after(
                    2000,
                    lambda: self.copy_local_btn.config(text=t("btn_copy"), fg=theme.FG_COLOR)
                    if self.copy_local_btn.winfo_exists()
                    else None,
                )

    def _copy_join_key(self) -> None:
        """Küme Katılım Anahtarını panoya kopyalar."""
        if self.join_key:
            self.clipboard_clear()
            self.clipboard_append(self.join_key)
            if hasattr(self, "copy_join_btn"):
                self.copy_join_btn.config(text=t("btn_copied_inline"))
                self.after(
                    2000,
                    lambda: self.copy_join_btn.config(text=t("btn_copy_join_key"))
                    if self.copy_join_btn.winfo_exists()
                    else None,
                )

    def _paste_device_id(self) -> None:
        try:
            clip = self.clipboard_get().strip()
            if clip:
                self.device_id_var.set(clip)
        except Exception:
            pass

    def _on_device_id_change(self, *_args) -> None:
        val = self.device_id_var.get().strip().upper()
        if not val:
            self.device_id_hint.config(
                text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
                fg=theme.FG_DISABLED,
            )
            return
        if re.match(constants.DEVICE_ID_REGEX, val):
            self.device_id_hint.config(text=t("sync_device_valid"), fg=theme.SUCCESS_COLOR)
        else:
            self.device_id_hint.config(text=t("sync_device_invalid_live"), fg=theme.WARNING_COLOR)

    def _center_window(self) -> None:
        """Pencereyi ekranın ortasına konumlandırır."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 700) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"+{x}+{y}")

    def _refresh_paired_nodes(self) -> None:
        """Eşleşmiş yedek düğümleri arka planda sorgulayıp listeler."""
        engine = getattr(self.controller, "installer_engine", None) if self.controller else None
        if not engine:
            self._render_paired_nodes([])
            return

        def _worker():
            nodes = engine.get_paired_nodes()
            if self.winfo_exists():
                self.after(0, lambda: self._render_paired_nodes(nodes))

        threading.Thread(target=_worker, daemon=True).start()

    def _render_paired_nodes(self, nodes: list[dict]) -> None:
        if not self.winfo_exists():
            return
        for child in self.nodes_list_frame.winfo_children():
            child.destroy()

        if not nodes:
            empty_lbl = StyledLabel(
                self.nodes_list_frame,
                text=t("node_dialog_no_nodes"),
                font=theme.FONT_SMALL,
                fg=theme.FG_DISABLED,
                bg=theme.BG_SECONDARY,
            )
            empty_lbl.pack(anchor=tk.W, pady=6)
            return

        for node in nodes[:4]:
            did = node.get("device_id", "")
            connected = node.get("connected", False)

            row = tk.Frame(
                self.nodes_list_frame,
                bg=theme.ENTRY_BG,
                padx=10,
                pady=5,
                highlightthickness=1,
                highlightbackground=theme.CARD_BORDER,
            )
            row.pack(fill=tk.X, pady=(0, 4))

            rem_btn = DangerButton(
                row,
                text=t("btn_remove_node"),
                command=lambda d=did: self._on_remove_node(d),
                width=9,
                pady=2,
                font=theme.FONT_SMALL_BOLD,
            )
            rem_btn.pack(side=tk.RIGHT, padx=(8, 0))

            status_txt = t("node_status_online") if connected else t("node_status_waiting")
            status_col = theme.SUCCESS_COLOR if connected else theme.WARNING_COLOR
            st_lbl = StyledLabel(
                row,
                text=status_txt,
                font=theme.FONT_SMALL_BOLD,
                fg=status_col,
                bg=theme.ENTRY_BG,
            )
            st_lbl.pack(side=tk.RIGHT, padx=(8, 0))

            short_did = did if len(did) <= 38 else f"{did[:23]}...{did[-12:]}"
            id_lbl = StyledLabel(
                row,
                text=short_did,
                font=theme.FONT_MONO_SMALL,
                fg=theme.FG_COLOR,
                bg=theme.ENTRY_BG,
                anchor=tk.W,
            )
            id_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_remove_node(self, device_id: str) -> None:
        engine = getattr(self.controller, "installer_engine", None) if self.controller else None
        if not engine:
            return

        self.status_label.config(text=t("settings_applying"), fg=theme.INFO_COLOR)

        def _worker():
            try:
                engine.remove_secondary_node(device_id)
                if self.winfo_exists():
                    self.after(0, self._on_remove_success)
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda err=str(e): self.status_label.config(
                        text=t("err_pairing_failed", error=err), fg=theme.ERROR_COLOR
                    ))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_remove_success(self) -> None:
        if not self.winfo_exists():
            return
        self.status_label.config(text=t("msg_node_removed"), fg=theme.SUCCESS_COLOR)
        self._refresh_paired_nodes()
        if self.controller:
            finish_page = self.controller._pages.get("finish")
            if finish_page and hasattr(finish_page, "refresh_health_status"):
                finish_page.refresh_health_status()

    def _on_add_clicked(self) -> None:
        """Ekle butonuna tıklandığında arka planda eşleştirir."""
        device_id = self.device_id_var.get().strip().upper()

        if not device_id:
            messagebox.showerror(t("msg_invalid_input"), t("err_no_device_id"), parent=self)
            return

        if not re.match(constants.DEVICE_ID_REGEX, device_id):
            messagebox.showerror(
                t("msg_invalid_input"),
                t("err_invalid_device_id"),
                parent=self,
            )
            return

        if self.local_device_id and device_id == self.local_device_id:
            messagebox.showerror(
                t("msg_invalid_input"),
                t("err_self_device_id"),
                parent=self,
            )
            return

        engine = getattr(self.controller, "installer_engine", None) if self.controller else None
        if not engine:
            self.status_label.config(text=t("err_no_engine"), fg=theme.ERROR_COLOR)
            return

        self.add_btn.set_state("disabled")
        self.status_label.config(text=t("msg_pairing"), fg=theme.INFO_COLOR)

        def _worker():
            try:
                engine.add_secondary_node(device_id)
                if self.winfo_exists():
                    self.after(0, self._on_add_success)
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda err=str(e): self._on_add_error(err))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_add_success(self) -> None:
        if not self.winfo_exists():
            return
        self.add_btn.set_state("normal")
        self.status_label.config(text=t("msg_pairing_ok"), fg=theme.SUCCESS_COLOR)
        self.device_id_entry.delete(0, tk.END)
        self._refresh_paired_nodes()

        if self.controller:
            finish_page = self.controller._pages.get("finish")
            if finish_page and hasattr(finish_page, "refresh_health_status"):
                finish_page.refresh_health_status()

    def _on_add_error(self, error_msg: str) -> None:
        if not self.winfo_exists():
            return
        self.add_btn.set_state("normal")
        self.status_label.config(
            text=t("err_pairing_failed", error=error_msg),
            fg=theme.ERROR_COLOR,
        )