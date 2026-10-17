"""
Yedek Node Ekleme Diyaloğu.

Merkez bilgisayarda, kurulum tamamlandıktan sonra yeni bir yedek düğümü
(bilgisayarı) Syncthing ağına eklemek için kullanılır.
"""

import re
import tkinter as tk
from tkinter import messagebox

from gui import theme
from gui.widgets import (
    CardFrame,
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
    Yedek node ekleme diyaloğu.

    Kullanıcı, yedek bilgisayarın Syncthing Device ID'sini girer ve
    'Ekle ve Eşleştir' butonuna basar. Syncthing API üzerinden cihaz eşleştirme
    ve klasör paylaşımı yapılır.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.title(t("node_dialog_title"))
        self.geometry("680x500")
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
        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=theme.PADDING_LARGE)
        content.pack(fill=tk.BOTH, expand=True)

        title_label = StyledLabel(
            content,
            text=t("node_dialog_title"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(anchor=tk.W, pady=(0, 4))

        desc_label = StyledLabel(
            content,
            text=t("node_dialog_desc"),
            font=theme.FONT_NORMAL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=620,
            justify=tk.LEFT,
        )
        desc_label.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

        # ─── Ana Bilgisayar Cihaz ID Kartı ──────────────────────────
        self.local_device_id = ""
        try:
            from core.config_manager import ConfigManager

            saved = ConfigManager().load()
            self.local_device_id = saved.get("local_device_id", "")
        except Exception:
            pass

        if not self.local_device_id and self.controller and hasattr(self.controller, "installer_engine"):
            try:
                self.local_device_id = self.controller.installer_engine.syncthing_service.get_device_id()
            except Exception:
                pass

        if self.local_device_id:
            local_card = CardFrame(content)
            local_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

            local_title = StyledLabel(
                local_card,
                text=t("node_dialog_local_id_title"),
                font=theme.FONT_SMALL_BOLD,
                fg=theme.FG_SECONDARY,
                bg=theme.BG_SECONDARY,
            )
            local_title.pack(anchor=tk.W)

            local_row = tk.Frame(local_card, bg=theme.BG_SECONDARY)
            local_row.pack(fill=tk.X, pady=(6, 0))

            self.copy_local_btn = SecondaryButton(
                local_row,
                text=t("btn_copy"),
                command=self._copy_local_id,
                width=12,
            )
            self.copy_local_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

            local_id_lbl = StyledLabel(
                local_row,
                text=self.local_device_id,
                font=theme.FONT_MONO_SMALL,
                fg=theme.ACCENT_COLOR,
                bg=theme.ENTRY_BG,
                padx=8,
                pady=6,
                anchor=tk.W,
            )
            local_id_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── Eklenecek Yedek Device ID Kartı ────────────────────────
        device_card = CardFrame(content, border_color=theme.ACCENT_COLOR)
        device_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        device_label = StyledLabel(
            device_card,
            text=t("node_dialog_input_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_label.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        input_row = tk.Frame(device_card, bg=theme.BG_SECONDARY)
        input_row.pack(fill=tk.X)

        paste_btn = SecondaryButton(
            input_row,
            text=t("btn_paste"),
            command=self._paste_device_id,
            width=10,
        )
        paste_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

        self.device_id_var = tk.StringVar()
        self.device_id_entry = StyledEntry(
            input_row,
            textvariable=self.device_id_var,
            font=theme.FONT_MONO_SMALL,
            width=54,
        )
        self.device_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        self.device_id_hint = StyledLabel(
            device_card,
            text="Format: AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH",
            font=theme.FONT_SMALL,
            fg=theme.FG_DISABLED,
            bg=theme.BG_SECONDARY,
            wraplength=580,
            justify=tk.LEFT,
            anchor=tk.W,
        )
        self.device_id_hint.pack(anchor=tk.W, pady=(6, 0))
        self.device_id_var.trace_add("write", self._on_device_id_change)

        # ─── Durum / Bilgi ──────────────────────────────────────────
        self.status_label = StyledLabel(
            content,
            text="",
            font=theme.FONT_NORMAL_BOLD,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=600,
            justify=tk.LEFT,
        )
        self.status_label.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

        # ─── Butonlar ───────────────────────────────────────────────
        footer = tk.Frame(content, bg=theme.BG_COLOR)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        cancel_btn = SecondaryButton(
            footer,
            text=t("btn_cancel"),
            command=self.destroy,
            width=12,
        )
        cancel_btn.pack(side=tk.LEFT)

        add_btn = PrimaryButton(
            footer,
            text=t("node_dialog_btn_add"),
            command=self._on_add_clicked,
            width=18,
        )
        add_btn.pack(side=tk.RIGHT)

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
        x = (self.winfo_screenwidth() - 680) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")

    def _on_add_clicked(self) -> None:
        """Ekle butonuna tıklandığında."""
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

        if self.controller:
            engine = getattr(self.controller, "installer_engine", None)
            if engine:
                try:
                    self.status_label.config(
                        text=t("msg_pairing"),
                        fg=theme.INFO_COLOR,
                    )
                    self.update_idletasks()
                    engine.add_secondary_node(device_id)
                    self.status_label.config(
                        text=t("msg_pairing_ok"),
                        fg=theme.SUCCESS_COLOR,
                    )
                    self.device_id_entry.delete(0, tk.END)

                    finish_page = self.controller._pages.get("finish")
                    if finish_page and hasattr(finish_page, "refresh_health_status"):
                        finish_page.refresh_health_status()
                except Exception as e:
                    self.status_label.config(
                        text=t("err_pairing_failed", error=str(e)),
                        fg=theme.ERROR_COLOR,
                    )
            else:
                self.status_label.config(
                    text=t("err_no_engine"),
                    fg=theme.ERROR_COLOR,
                )