"""
Kurulum ilerleme sayfası.

5 aşamalı görsel bileşen durumu (NSSM, Caddy, Cloudflared, Syncthing, Güvenlik Duvarı),
ProgressBar, renkli terminal log alanı ve iptal/tekrar dene yönetimi içerir.
"""

import queue
import tkinter as tk
from tkinter import ttk

from gui import theme
from gui.base_page import BasePage
from gui.dialogs.error_dialog import ErrorDialog
from gui.widgets import (
    CardFrame,
    HeaderFrame,
    PrimaryButton,
    SecondaryButton,
    StyledLabel,
    StyledProgressbar,
    StyledText,
)
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger(__name__)


class InstallPage(BasePage):
    """4. Adım: Kurulum ilerleme ekranı."""

    PAGE_NAME = "install"

    STAGE_THRESHOLDS = [
        ("stage_nssm", 5, 10),
        ("stage_caddy", 10, 35),
        ("stage_cloudflared", 35, 60),
        ("stage_syncthing", 60, 88),
        ("stage_firewall", 88, 100),
    ]

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.engine = None
        self.progress_queue: queue.Queue | None = None
        self._is_running = False
        self._last_device_id = ""
        self._stage_labels: list[tk.Label] = []

        self._build_ui()

    def _build_ui(self) -> None:
        """Sayfa arayüzünü oluşturur."""
        header = HeaderFrame(
            self,
            title=t("install_title"),
            subtitle=t("install_subtitle"),
        )
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(16, 8))

        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=(0, 8))

        # ─── Durum & 5 Aşamalı İlerleme Kartı ───────────────────
        status_card = CardFrame(content, padx=16, pady=12)
        status_card.pack(fill=tk.X, pady=(0, 10))

        # 5 Aşamalı Bileşen Göstergesi
        stages_row = tk.Frame(status_card, bg=theme.BG_SECONDARY)
        stages_row.pack(fill=tk.X, pady=(0, 10))
        for col in range(5):
            stages_row.grid_columnconfigure(col, weight=1, uniform="stage_col")

        self._stage_labels.clear()
        for idx, (stage_key, _, _) in enumerate(self.STAGE_THRESHOLDS):
            pad_l = 0 if idx == 0 else 3
            pad_r = 0 if idx == 4 else 3
            lbl = tk.Label(
                stages_row,
                text=t(stage_key),
                font=theme.FONT_SMALL_BOLD,
                fg=theme.FG_DISABLED,
                bg=theme.BG_TERTIARY,
                padx=8,
                pady=5,
            )
            lbl.grid(row=0, column=idx, sticky="ew", padx=(pad_l, pad_r))
            self._stage_labels.append(lbl)

        status_row = tk.Frame(status_card, bg=theme.BG_SECONDARY)
        status_row.pack(fill=tk.X, pady=(0, 6))

        self.status_label = StyledLabel(
            status_row,
            text=t("install_preparing"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.status_label.pack(side=tk.LEFT)

        self.percent_label = StyledLabel(
            status_row,
            text="%0",
            font=theme.FONT_MEDIUM,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.percent_label.pack(side=tk.RIGHT)

        self.progress_bar = StyledProgressbar(
            status_card,
            maximum=100,
            length=500,
        )
        self.progress_bar.pack(fill=tk.X)

        # ─── Renkli Terminal Log Kartı ──────────────────────────
        log_card = CardFrame(content, padx=16, pady=12)
        log_card.pack(fill=tk.BOTH, expand=True)

        log_title = StyledLabel(
            log_card,
            text=t("install_log_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        log_title.pack(anchor=tk.W, pady=(0, 6))

        log_container = tk.Frame(log_card, bg=theme.LOG_BG)
        log_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = StyledText(
            log_container,
            width=theme.LOG_WIDTH,
            height=11,
            yscrollcommand=scrollbar.set,
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # ─── Alt Butonlar ───────────────────────────────────────
        self.footer = tk.Frame(content, bg=theme.BG_COLOR)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 8))

        self.back_btn = SecondaryButton(
            self.footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=14,
        )

        self.cancel_btn = SecondaryButton(
            self.footer,
            text=t("btn_cancel"),
            command=self._on_cancel,
            width=14,
        )
        self.cancel_btn.pack(side=tk.RIGHT)

        self.retry_btn = PrimaryButton(
            self.footer,
            text=t("btn_retry"),
            command=self.start_installation,
            width=16,
        )

    def _update_stage_pills(self, percentage: int) -> None:
        """Yüzde ilerlemesine göre 5 aşama kutusunu renklendirir."""
        for idx, (stage_key, start_pct, end_pct) in enumerate(self.STAGE_THRESHOLDS):
            if idx >= len(self._stage_labels):
                break
            lbl = self._stage_labels[idx]
            base_text = t(stage_key)
            short_title = base_text.split(".", 1)[-1].strip()
            if percentage >= end_pct:
                lbl.config(
                    text=f"✓ {short_title}",
                    fg=theme.SUCCESS_COLOR,
                    bg=theme.BG_TERTIARY,
                )
            elif percentage >= start_pct:
                lbl.config(
                    text=f"● {short_title}",
                    fg=theme.BUTTON_TEXT,
                    bg=theme.BUTTON_PRIMARY_BG,
                )
            else:
                lbl.config(
                    text=base_text,
                    fg=theme.FG_DISABLED,
                    bg=theme.BG_TERTIARY,
                )

    def set_engine(self, engine) -> None:
        """InstallerEngine referansını bağlar."""
        self.engine = engine
        self.progress_queue = engine.progress_queue
        logger.debug("InstallerEngine kurulum sayfasına bağlandı")

    def _on_cancel(self) -> None:
        """Kurulumu iptal et."""
        if self.engine and self._is_running:
            self.engine.cancel()
            self.log_text.append_text(f"\n{t('install_cancelling_log')}")
            self.status_label.config(text=t("install_cancelling"), fg=theme.WARNING_COLOR)
            self.cancel_btn.set_state("disabled")

    def set_progress(self, value: int, message: str) -> None:
        """İlerleme durumunu günceller."""
        if value >= 0:
            self.progress_bar.set_progress(value)
            self.percent_label.config(text=f"%{value}")
            self._update_stage_pills(value)
        self.status_label.config(text=message)
        self.log_text.append_text(f"✓ {message}")

    def start_installation(self) -> None:
        """Kurulumu başlatır."""
        self.back_btn.pack_forget()
        self.retry_btn.pack_forget()
        self.cancel_btn.config(text=t("btn_cancel"), command=self._on_cancel)
        self.cancel_btn.set_state("normal")
        self.status_label.config(text=t("install_preparing"), fg=theme.FG_COLOR)
        self.progress_bar.set_progress(0)
        self.percent_label.config(text="%0")
        self._update_stage_pills(0)

        if self.engine:
            self._is_running = True
            self.log_text.clear()
            config = self.controller.build_install_config()
            self.log_text.append_text(f"● {t('install_preparing')}")
            self.engine.start(config)
            self._poll_progress()

    def _poll_progress(self) -> None:
        """GUI thread'de çalışır, queue'yu 100ms aralıklarla kontrol eder."""
        if not self.progress_queue:
            return

        try:
            while True:
                event = self.progress_queue.get_nowait()
                if event.is_error:
                    self._on_error(event.message)
                    return
                if event.is_complete:
                    self._on_complete()
                    return
                if event.is_cancelled:
                    self._on_cancelled()
                    return
                self.set_progress(event.percentage, event.message)
        except queue.Empty:
            pass

        if self._is_running:
            self.after(100, self._poll_progress)

    def _on_error(self, message: str) -> None:
        """Hata durumunu göster."""
        self._is_running = False
        self.status_label.config(text=t("install_failed"), fg=theme.ERROR_COLOR)
        self.log_text.append_text(f"\n{t('install_error_prefix', message=message)}")
        self.cancel_btn.config(text=t("btn_close"), command=self._close_window)
        self.cancel_btn.set_state("normal")
        self.back_btn.pack(side=tk.LEFT)
        self.retry_btn.pack(side=tk.RIGHT, padx=(0, theme.PADDING_SMALL))

        try:
            if self.winfo_ismapped():
                ErrorDialog(self, t("install_failed"), message)
        except Exception:
            pass

    def _on_complete(self) -> None:
        """Kurulum tamamlandı."""
        self._is_running = False
        self.status_label.config(text=t("install_complete"), fg=theme.SUCCESS_COLOR)
        self.progress_bar.set_progress(100)
        self.percent_label.config(text="%100")
        self._update_stage_pills(100)
        self.log_text.append_text(f"\n{t('install_complete_log')}")
        self.cancel_btn.set_state("disabled")

        self.after(800, self._go_to_finish)

    def _on_cancelled(self) -> None:
        """Kurulum iptal edildi."""
        self._is_running = False
        self.status_label.config(text=t("install_cancelled"), fg=theme.WARNING_COLOR)
        self.log_text.append_text(f"\n{t('install_cancelled_log')}")
        self.cancel_btn.config(text=t("btn_close"), command=self._close_window)
        self.cancel_btn.set_state("normal")
        self.back_btn.pack(side=tk.LEFT)
        self.retry_btn.pack(side=tk.RIGHT, padx=(0, theme.PADDING_SMALL))

    def _go_to_finish(self) -> None:
        """Bitiş sayfasına geçer."""
        self.controller.next_page()

    def _close_window(self) -> None:
        """Uygulamayı kapatır."""
        self.controller.destroy()

    def on_enter(self) -> None:
        """Sayfaya girildiğinde kurulumu başlat."""
        self.start_installation()

    def on_leave(self) -> None:
        """Sayfadan ayrılırken polling'i durdur."""
        self._is_running = False