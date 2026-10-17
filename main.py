"""
AutoHomeWebSetup - Uygulama Giriş Noktası

UAC yönetici yetkisi kontrolü yapar ve uygulamayı başlatır.
"""

import sys
import traceback

from utils.platform_utils import ensure_admin


def main() -> int:
    """
    Uygulamanın ana giriş noktası.

    Returns:
        int: Çıkış kodu (0: başarılı)
    """
    # HATA-10: Logger'ı modül seviyesinde değil, dizinler oluşturulduktan SONRA başlat
    from utils.logger import get_logger

    # Yönetici yetkisi kontrolü
    ensure_admin()

    # Uygulama dizinlerini oluştur
    from utils.platform_utils import create_app_directories

    create_app_directories()

    # Logger'ı dizinler oluşturulduktan sonra başlat
    logger = get_logger(__name__)
    logger.info("AutoHomeWebSetup başlatılıyor...")

    # Ana uygulamayı başlat
    try:
        from app import App

        app = App()
        app.run()
    except Exception:
        logger.exception("Uygulama başlatılırken kritik hata oluştu")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())