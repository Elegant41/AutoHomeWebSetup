"""
Tüm sihirbaz sayfaları için temel sınıf.

Sayfa geçiş validasyonu, giriş/çıkış hook'ları ve veri toplama
işlevlerini tanımlar.
"""

import tkinter as tk
from typing import Any

from gui import theme


class BasePage(tk.Frame):
    """
    Tüm sihirbaz sayfaları için temel sınıf.

    Alt sınıflar şu metotları override edebilir:
        - validate(): Sayfa geçiş validasyonu
        - on_enter(): Sayfa gösterildiğinde çağrılır
        - on_leave(): Sayfadan ayrılırken çağrılır
        - get_data(): Sayfadaki kullanıcı verilerini döndürür
    """

    # Sayfa kimliği (kayıt için)
    PAGE_NAME = "base"

    def __init__(self, parent, controller):
        """
        Args:
            parent: Ana container frame
            controller: App sınıfı referansı
        """
        super().__init__(parent, bg=theme.BG_COLOR)
        self.controller = controller
        self._data: dict[str, Any] = {}

    def validate(self) -> tuple[bool, str]:
        """
        Sayfa geçiş validasyonu.

        Returns:
            (True, "") başarılıysa, (False, hata_mesajı) başarısızsa
        """
        return True, ""

    def on_enter(self) -> None:
        """Sayfa gösterildiğinde çağrılır."""
        pass

    def on_leave(self) -> None:
        """Sayfadan ayrılırken çağrılır."""
        pass

    def get_data(self) -> dict[str, Any]:
        """
        Sayfadaki kullanıcı verilerini döndürür.

        Returns:
            dict: Sayfa verileri
        """
        return self._data

    def set_data(self, data: dict[str, Any]) -> None:
        """Sayfa verilerini ayarlar."""
        self._data = data

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def next_page(self) -> None:
        """Validasyonu yapıp bir sonraki sayfaya geçer."""
        valid, error_msg = self.validate()
        if not valid:
            self._show_validation_error(error_msg)
            return

        # Verileri controller'a kaydet
        self.controller.collect_page_data(self.PAGE_NAME, self.get_data())
        self.controller.next_page()

    def prev_page(self) -> None:
        """Bir önceki sayfaya döner."""
        self.controller.prev_page()

    def _show_validation_error(self, message: str) -> None:
        """Validasyon hatasını durum etiketi veya diyalogla gösterir."""
        # Alt sınıflar kendi hata gösterimini yapabilir
        self._display_error(message)

    def _display_error(self, message: str) -> None:
        """Varsayılan hata gösterimi. Alt sınıflar override edebilir."""
        import tkinter.messagebox as messagebox
        from utils.i18n import t

        messagebox.showerror(t("msg_invalid_input"), message, parent=self)

    def _display_info(self, title: str, message: str) -> None:
        """Bilgi mesajı gösterir."""
        import tkinter.messagebox as messagebox

        messagebox.showinfo(title, message, parent=self)