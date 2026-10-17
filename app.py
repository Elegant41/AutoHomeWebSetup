"""
AutoHomeWebSetup - Ana Uygulama Sınıfı

Wizard orkestratörü. Tkinter ana penceresini yönetir ve
sihirbaz sayfalarının geçişlerini kontrol eder.
"""

import queue
import tkinter as tk

from core.models import InstallConfig, NodeRole
from utils import constants
from utils.logger import get_logger, setup_gui_logging

logger = get_logger(__name__)


class App(tk.Tk):
    """
    Ana uygulama sınıfı.

    Tkinter kök penceresini oluşturur ve sihirbaz sayfalarını yönetir.
    """

    def __init__(self):
        super().__init__()

        # Pencere yapılandırması
        from gui import theme
        from gui.widgets import WizardStepBar

        self.title(constants.WINDOW_TITLE)
        self.configure(bg=theme.BG_COLOR)
        self.geometry(f"{constants.WINDOW_WIDTH}x{constants.WINDOW_HEIGHT}")
        self.minsize(constants.WINDOW_MIN_WIDTH, constants.WINDOW_MIN_HEIGHT)
        self.resizable(True, True)

        # Pencere ikonu ve koyu başlık çubuğu
        try:
            from utils.resource_path import resource_path
            icon_path = resource_path("assets/icon.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass
        theme.apply_dark_titlebar(self)

        # Merkezde konumlandır
        self._center_window()

        # Sayfa yığını (wizard stack)
        self._page_stack: list[tk.Frame] = []
        self._pages: dict[str, tk.Frame] = {}

        # Sayfa verileri (her sayfanın kayıtlı verileri)
        self._page_data: dict[str, dict] = {}

        # GUI log kuyruğu
        self.log_queue: queue.Queue = queue.Queue()
        setup_gui_logging(self.log_queue)

        # Üst Adım Çubuğu (Stepper Bar)
        self._step_bar = WizardStepBar(self, self)
        self._step_bar.pack(fill=tk.X, side=tk.TOP)

        # Ana içerik container'ı
        self._container = tk.Frame(self, bg=theme.BG_COLOR)
        self._container.pack(fill=tk.BOTH, expand=True)

        # Installer engine (worker thread + progress queue)
        from core.installer import InstallerEngine

        self.installer_engine = InstallerEngine()

        # Sayfaları oluştur ve kaydet
        self._init_pages()

        # Kurulum sayfasına engine'i bağla
        install_page = self._pages.get("install")
        if hasattr(install_page, "set_engine"):
            install_page.set_engine(self.installer_engine)

        logger.info("Ana pencere oluşturuldu")

    def _center_window(self) -> None:
        """Pencereyi ekranın ortasına konumlandırır."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - constants.WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - constants.WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

    def _init_pages(self) -> None:
        """Tüm sihirbaz sayfalarını oluşturur ve kaydeder."""
        from gui.pages.welcome_page import WelcomePage
        from gui.pages.server_settings_page import ServerSettingsPage
        from gui.pages.sync_settings_page import SyncSettingsPage
        from gui.pages.install_page import InstallPage
        from gui.pages.finish_page import FinishPage

        self.register_page(WelcomePage.PAGE_NAME, WelcomePage(self._container, self))
        self.register_page(SyncSettingsPage.PAGE_NAME, SyncSettingsPage(self._container, self))
        self.register_page(ServerSettingsPage.PAGE_NAME, ServerSettingsPage(self._container, self))
        self.register_page(InstallPage.PAGE_NAME, InstallPage(self._container, self))
        self.register_page(FinishPage.PAGE_NAME, FinishPage(self._container, self))

        # İlk sayfayı göster
        self.show_page(WelcomePage.PAGE_NAME)

    # ─── Sayfa Yönetimi ─────────────────────────────────────────────
    def register_page(self, name: str, page: tk.Frame) -> None:
        """Bir sayfayı kaydeder."""
        self._pages[name] = page

    def show_page(self, name: str) -> None:
        """Belirtilen sayfayı gösterir."""
        page = self._pages.get(name)
        if page is None:
            raise ValueError(f"Sayfa bulunamadı: {name}")

        # Önceki sayfayı gizle
        if self._page_stack:
            current = self._page_stack[-1]
            if current is page:  # Zaten bu sayfa gösterimde
                return
            try:
                current.pack_forget()
                if hasattr(current, "on_leave"):
                    current.on_leave()
            except Exception as e:
                logger.error(f"{current.PAGE_NAME} sayfasından çıkılırken hata: {e}")

        # Yeni sayfayı göster
        try:
            page.pack(fill=tk.BOTH, expand=True)
            page.tkraise()
            # Eğer stack'te zaten varsa (geri navigasyon) ekleme
            if not self._page_stack or self._page_stack[-1] is not page:
                self._page_stack.append(page)

            if hasattr(self, "_step_bar") and self._step_bar:
                self._step_bar.set_active_step(name)

            if hasattr(page, "on_enter"):
                page.on_enter()
        except Exception as e:
            logger.error(f"{page.PAGE_NAME} sayfasına girilirken hata: {e}")
            import traceback
            traceback.print_exc()

    def next_page(self) -> None:
        """
        Sıradaki sayfaya geçer.
        Sıralama: welcome → sync_settings → server_settings → install → finish
        """
        order = [
            "welcome",
            "sync_settings",
            "server_settings",
            "install",
            "finish",
        ]

        if not self._page_stack:
            return

        current_name = self._find_page_name(self._page_stack[-1])
        if current_name is None:
            return

        try:
            current_index = order.index(current_name)
        except ValueError:
            return

        if current_index + 1 < len(order):
            next_name = order[current_index + 1]
            self.show_page(next_name)

    def prev_page(self) -> None:
        """Bir önceki sayfaya döner."""
        if len(self._page_stack) <= 1:
            return

        current = self._page_stack.pop()
        try:
            current.pack_forget()
            if hasattr(current, "on_leave"):
                current.on_leave()
        except Exception as e:
            logger.error(f"{current.PAGE_NAME} sayfasından çıkılırken hata: {e}")

        previous = self._page_stack[-1]
        try:
            previous.pack(fill=tk.BOTH, expand=True)
            previous.tkraise()
            prev_name = self._find_page_name(previous)
            if prev_name and hasattr(self, "_step_bar") and self._step_bar:
                self._step_bar.set_active_step(prev_name)
            if hasattr(previous, "on_enter"):
                previous.on_enter()
        except Exception as e:
            logger.error(f"{previous.PAGE_NAME} sayfasına girilirken hata: {e}")

    def go_to_page(self, name: str) -> None:
        """Belirtilen sayfaya doğrudan geçer (back stack temizlenir)."""
        if self._page_stack:
            current = self._page_stack[-1]
            try:
                current.pack_forget()
                if hasattr(current, "on_leave"):
                    current.on_leave()
            except Exception as e:
                logger.error(f"{current.PAGE_NAME} sayfasından çıkılırken hata: {e}")

        self._page_stack.clear()
        self.show_page(name)

    def _find_page_name(self, page: tk.Frame) -> str | None:
        """Sayfa nesnesinin adını bulur."""
        for name, registered in self._pages.items():
            if registered is page:
                return name
        return None

    def change_language(self, lang_code: str) -> None:
        """Uygulama dilini değiştirir ve arayüzü yeniden yükler (form verilerini ve geçmişi korur)."""
        if self.installer_engine.is_running():
            return

        from utils.i18n import set_language
        set_language(lang_code)

        # Mevcut sayfanın anlık verilerini kaydet ve sayfa geçmişini hatırla
        stack_names: list[str] = []
        if self._page_stack:
            current = self._page_stack[-1]
            current_name = self._find_page_name(current)
            if current_name and hasattr(current, "get_data"):
                try:
                    self.collect_page_data(current_name, current.get_data())
                except Exception:
                    pass
            for p in self._page_stack:
                pname = self._find_page_name(p)
                if pname:
                    stack_names.append(pname)

        # Mevcut sayfaları ve üst çubuğu temizle
        if hasattr(self, "_step_bar") and self._step_bar:
            self._step_bar.destroy()
        from gui.widgets import WizardStepBar
        self._step_bar = WizardStepBar(self, self)
        self._step_bar.pack(fill=tk.X, side=tk.TOP, before=self._container)

        for widget in self._container.winfo_children():
            widget.destroy()

        self._page_stack.clear()
        self._pages.clear()

        # Sayfaları yeni dille tekrar oluştur
        self._init_pages()

        # Kurulum sayfasına engine'i yeniden bağla
        install_page = self._pages.get("install")
        if hasattr(install_page, "set_engine"):
            install_page.set_engine(self.installer_engine)

        # Sayfa yığınını (back history) koruyarak kaldığımız sayfaya git
        if stack_names:
            self._page_stack.clear()
            for pname in stack_names[:-1]:
                if pname in self._pages:
                    self._page_stack.append(self._pages[pname])
            target_name = stack_names[-1]
            if target_name in self._pages:
                # Welcome sayfası _init_pages içinde açıldığı için gizle
                welcome_page = self._pages.get("welcome")
                if welcome_page and target_name != "welcome":
                    welcome_page.pack_forget()
                self.show_page(target_name)

    # ─── Veri Yönetimi ──────────────────────────────────────────────
    def collect_page_data(self, page_name: str, data: dict) -> None:
        """Bir sayfanın verilerini kaydeder."""
        self._page_data[page_name] = data

    def get_saved_page_data(self, page_name: str) -> dict:
        """Bir sayfanın kayıtlı verilerini döndürür."""
        return self._page_data.get(page_name, {})

    def build_install_config(self) -> InstallConfig:
        """Tüm sayfa verilerinden (veya mevcut kurulumdan) InstallConfig oluşturur."""
        config = InstallConfig()

        # Önce diskte kayıtlı konfigürasyon varsa varsayılan olarak yükle
        saved: dict = {}
        try:
            from core.config_manager import ConfigManager
            saved = ConfigManager().load()
        except Exception:
            pass

        # Sunucu ayarları
        server_data = self._page_data.get("server_settings", {})
        config.site_root_path = server_data.get("site_root_path") or saved.get("site_root_path", "")
        config.cloudflare_token = server_data.get("cloudflare_token") or saved.get("cloudflare_token", "")
        config.public_domain = server_data.get("public_domain") if "public_domain" in server_data else saved.get("public_domain", "")
        config.caddy_port = server_data.get("caddy_port") or saved.get("caddy_port", constants.CADDY_DEFAULT_PORT)
        config.prevent_sleep = server_data.get("prevent_sleep", saved.get("prevent_sleep", True))

        # Senkronizasyon ayarları
        sync_data = self._page_data.get("sync_settings", {})
        role = sync_data.get("node_role") or saved.get("node_role", "primary")
        config.node_role = NodeRole(role) if role in ("primary", "secondary") else NodeRole.PRIMARY
        config.primary_device_id = sync_data.get("primary_device_id") or saved.get("primary_device_id", "")

        # Cihaz ID ve Syncthing bilgileri
        config.local_device_id = saved.get("local_device_id", "")
        config.syncthing_api_key = saved.get("syncthing_api_key", "")
        config.syncthing_gui_port = saved.get("syncthing_gui_port", constants.SYNCTHING_GUI_PORT)

        return config

    # ─── GUI Loglama ────────────────────────────────────────────────
    def poll_log_queue(self) -> None:
        """GUI log kuyruğunu poll eder (100ms aralıklarla)."""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                # Aktif sayfaya log ilet
                if self._page_stack:
                    current = self._page_stack[-1]
                    if hasattr(current, "log_text"):
                        current.log_text.append_text(msg)
        except queue.Empty:
            pass
        self.after(100, self.poll_log_queue)

    def run(self) -> None:
        """Ana tkinter event loop'unu başlatır."""
        logger.info("Uygulama başlatılıyor...")
        self.poll_log_queue()
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()