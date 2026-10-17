"""
Kurulum ilerleme sayfası.

ProgressBar, durum etiketi, log alanı ve iptal butonu içerir.
InstallerEngine ile thread-safe queue üzerinden iletişim kurar.
"""

import queue
import tkinter as tk

from gui import theme
from gui.base_page import BasePage
from gui.dialogs.error_dialog import ErrorDialog
from gui.widgets import (
    CardFrame,
    PrimaryButton,
    SecondaryButton,
    StyledLabel,
    StyledProgressbar,
    StyledText,
)
from utils.logger import get_logger
from utils.i18n import t

logger = get_logger(__name__)


class InstallPage(BasePage):
    """4. Adım: Kurulum ilerleme ekranı."""

    PAGE_NAME = "install"

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Faz 8: InstallerEngine bağlantısı
        self.engine = None
        self.progress_queue: queue.Queue | None = None
        self._is_running = False
        self._last_device_id = ""

        self._build_ui()

    # ─── UI Oluşturma ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        """Sayfa arayüzünü oluşturur."""
        # ─── Başlık ─────────────────────────────────────────────
        header = tk.Frame(self, bg=theme.BG_COLOR)
        header.pack(fill=tk.X, padx=theme.PADDING_LARGE, pady=(theme.PADDING_LARGE, theme.PADDING_MEDIUM))

        title_label = StyledLabel(
            header,
            text=t("install_title"),
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=theme.BG_COLOR,
        )
        title_label.pack(anchor=tk.W)

        subtitle_label = StyledLabel(
            header,
            text=t("install_subtitle"),
            font=theme.FONT_NORMAL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_COLOR,
            wraplength=600,
            justify=tk.LEFT,
        )
        subtitle_label.pack(anchor=tk.W, pady=(theme.PADDING_XS, 0))

        # ─── İçerik ─────────────────────────────────────────────
        content = tk.Frame(self, bg=theme.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=theme.PADDING_LARGE, pady=theme.PADDING_MEDIUM)

        # ─── Durum Kartı ────────────────────────────────────────
        status_card = CardFrame(content)
        status_card.pack(fill=tk.X, pady=(0, theme.PADDING_MEDIUM))

        self.status_label = StyledLabel(
            status_card,
            text=t("install_preparing"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        self.status_label.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

        self.progress_bar = StyledProgressbar(
            status_card,
            maximum=100,
            length=500,
        )
        self.progress_bar.pack(fill=tk.X)

        self.percent_label = StyledLabel(
            status_card,
            text="%0",
            font=theme.FONT_SMALL,
            fg=theme.FG_SECONDARY,
            bg=theme.BG_SECONDARY,
        )
        self.percent_label.pack(anchor=tk.E, pady=(theme.PADDING_XS, 0))

        # ─── Log Kartı ──────────────────────────────────────────
        log_card = CardFrame(content)
        log_card.pack(fill=tk.BOTH, expand=True)

        log_title = StyledLabel(
            log_card,
            text=t("install_log_title"),
            font=theme.FONT_MEDIUM,
            fg=theme.FG_COLOR,
            bg=theme.BG_SECONDARY,
        )
        log_title.pack(anchor=tk.W, pady=(0, theme.PADDING_SMALL))

        self.log_text = StyledText(
            log_card,
            width=theme.LOG_WIDTH,
            height=12,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ─── Alt Butonlar ───────────────────────────────────────
        self.footer = tk.Frame(content, bg=theme.BG_COLOR)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, pady=theme.PADDING_MEDIUM)

        self.back_btn = SecondaryButton(
            self.footer,
            text=t("btn_back"),
            command=self.prev_page,
            width=12,
        )

        self.cancel_btn = SecondaryButton(
            self.footer,
            text=t("btn_cancel"),
            command=self._on_cancel,
            width=12,
        )
        self.cancel_btn.pack(side=tk.RIGHT)

        self.retry_btn = PrimaryButton(
            self.footer,
            text=t("btn_retry"),
            command=self.start_installation,
            width=14,
        )

    # ─── Engine Bağlantısı ──────────────────────────────────────────
    def set_engine(self, engine) -> None:
        """InstallerEngine referansını bağlar."""
        self.engine = engine
        self.progress_queue = engine.progress_queue
        logger.debug("InstallerEngine kurulum sayfasına bağlandı")

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
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

        if self.engine:
            self._is_running = True
            self.log_text.clear()
            config = self.controller.build_install_config()
            self.log_text.append_text(t("install_preparing"))
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

        # 100ms sonra tekrar kontrol et
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
        self.log_text.append_text(f"\n{t('install_complete_log')}")
        self.cancel_btn.set_state("disabled")

        # Bitiş sayfasına geç
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

    # ─── BasePage Override'ları ─────────────────────────────────────
    def on_enter(self) -> None:
        """Sayfaya girildiğinde kurulumu başlat."""
        self.start_installation()

    def on_leave(self) -> None:
        """Sayfadan ayrılırken polling'i durdur."""
        self._is_running = False