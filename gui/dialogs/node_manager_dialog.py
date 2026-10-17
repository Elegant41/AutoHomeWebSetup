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
        self.geometry("660x500")
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

        try:
            self.grab_set()
        except Exception:
            pass

        # Pencereyi merkeze konumlandır
        self._center_window()

        # ─── İçerik ─────────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR, padx=theme.PADDING_LARGE, pady=theme.PADDING_LARGE)
        content.pack(fill=tk.BOTH, expand=True)

        # ─── Başlık ─────────────────────────────────────────────────
        title_label = StyledLabel(
            content,
            text=t("node_dialog_title"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        desc_label = StyledLabel(
            content,
            text=t("node_dialog_desc"),
            font=theme.FONT_NORMAL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=600,
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
                font=theme.FONT_SMALL,
                fg=theme.FG_SECONDARY,
                bg=theme.BG_SECONDARY,
            )
            local_title.pack(anchor=tk.W)

            local_row = tk.Frame(local_card, bg=theme.BG_SECONDARY)
            local_row.pack(fill=tk.X, pady=(6, 0))

            # ÖNCE sağdaki Kopyala butonunu pack et ki uzun ID butonu ezmesin
            copy_btn = SecondaryButton(
                local_row,
                text=t("btn_copy"),
                command=self._copy_local_id,
                width=10,
            )
            copy_btn.pack(side=tk.RIGHT, padx=(theme.PADDING_SMALL, 0))

            local_id_lbl = StyledLabel(
                local_row,
                text=self.local_device_id,
                font=theme.FONT_MONO_SMALL,
                fg=theme.ACCENT_COLOR,
                bg=theme.BG_TERTIARY,
                padx=8,
                pady=6,
                anchor=tk.W,
            )
            local_id_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ─── Eklenecek Yedek Device ID Kartı ────────────────────────
        device_card = CardFrame(content)
        device_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        device_label = StyledLabel(
            device_card,
            text=t("node_dialog_input_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        device_label.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.device_id_var = tk.StringVar()
        self.device_id_entry = StyledEntry(
            device_card,
            textvariable=self.device_id_var,
            font=theme.FONT_MONO_SMALL,
            width=64,
        )
        self.device_id_entry.pack(fill=tk.X, ipady=4)

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
        self.device_id_hint.pack(anchor=tk.W, pady=(theme.PADDING_XS, 0))

        # ─── Durum / Bilgi ──────────────────────────────────────────
        self.status_label = StyledLabel(
            content,
            text="",
            font=theme.FONT_NORMAL,
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
            width=16,
        )
        add_btn.pack(side=tk.RIGHT)

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def _copy_local_id(self) -> None:
        """Ana bilgisayarın Device ID'sini panoya kopyalar."""
        if self.local_device_id:
            self.clipboard_clear()
            self.clipboard_append(self.local_device_id)
            messagebox.showinfo(t("msg_copied_title"), t("msg_copied_device_id"), parent=self)

    def _center_window(self) -> None:
        """Pencereyi ekranın ortasına konumlandırır."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 660) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"+{x}+{y}")

    def _on_add_clicked(self) -> None:
        """Ekle butonuna tıklandığında."""
        device_id = self.device_id_var.get().strip()

        # Validasyon
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

        # Kendi Cihaz ID'sini girmesini engelle
        if self.local_device_id and device_id == self.local_device_id:
            messagebox.showerror(
                t("msg_invalid_input"),
                "Kendi bilgisayarınızın Cihaz ID'sini girdiniz. Lütfen YEDEK bilgisayarın Cihaz ID'sini girin.",
                parent=self,
            )
            return

        # Syncthing API ile cihaz ekleme ve klasör paylaşma
        if self.controller:
            engine = getattr(self.controller, "installer_engine", None)
            if engine:
                try:
                    self.status_label.config(
                        text=t("msg_pairing"),
                        fg=theme.INFO_COLOR,
                    )
                    self.update_idletasks()
                    # Yedek düğümü Syncthing ağına ekle ve site klasörünü paylaş
                    engine.add_secondary_node(device_id)
                    self.status_label.config(
                        text=t("msg_pairing_ok"),
                        fg=theme.SUCCESS_COLOR,
                    )
                    self.device_id_entry.delete(0, tk.END)

                    # Bitiş sayfası açıksa canlı sağlık durumunu hemen güncelle
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