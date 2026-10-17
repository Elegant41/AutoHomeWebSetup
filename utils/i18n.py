"""
i18n (Internationalization) Modülü
Uygulamanın çift dil desteğini (TR/EN) sağlar.
"""

_CURRENT_LANG = "tr"

_TRANSLATIONS = {
    "tr": {
        # Genel Butonlar
        "btn_next": "İleri ▶",
        "btn_back": "◀ Geri",
        "btn_copy": "📋 Kopyala",
        "btn_browse": "📂 Gözat...",
        "btn_cancel": "İptal",
        "btn_close": "Kapat",
        "btn_save": "💾 Kaydet",
        "btn_settings": "⚙️ Ayarlar",
        "btn_refresh": "🔄 Durumu Yenile",
        "btn_uninstall": "🗑️ Kurulumu Kaldır",
        "btn_add_node": "➕ Yedek Ekle",
        "btn_start_install": "Kurulumu Başlat",
        "btn_retry": "🔄 Tekrar Dene",
        "btn_go_to_manage": "🚀 Kurulum Yönetimi & Düğüm Ekle",
        "btn_reinstall": "⚙️ Sıfırdan Yeniden Kur",
        "btn_open_site": "🌐 Siteyi Aç (http://localhost)",
        "btn_open_site_browser": "🌐 Web Sitesini Tarayıcıda Aç",

        # Hoşgeldiniz
        "welcome_title": "AHWS Setup",
        "welcome_subtitle": "Yüksek Erişilebilirlikli (HA) Statik Web Kurulum Sihirbazı",
        "welcome_desc": (
            "Bu sihirbaz, Caddy web sunucusu, Cloudflare Tunnel ve Syncthing servislerini otomatik olarak bilgisayarınıza kuracak ve yapılandıracaktır.\n\n"
            "İlerlemeden önce lütfen gerekli bilgilerin (Cloudflare Token vb.) hazır olduğundan emin olun."
        ),
        "welcome_existing_title": "✓ Mevcut Kurulum Bulundu",
        "welcome_existing_desc": "Bu bilgisayarda önceden tamamlanmış bir AHWS kurulumu tespit edildi. Tekrar kurulum yapmadan doğrudan yönetim ve düğüm ekleme ekranına geçebilirsiniz.",
        "finish_role": "Düğüm Rolü",
        "install_date_label": "Kurulum Tarihi",
        "device_id_short_label": "Cihaz ID",
        "unknown_label": "Bilinmiyor",
        "welcome_warning": "⚠ Bu işlem yönetici hakları gerektirir. Devam etmek için UAC uyarısını onaylayın.",

        # Sunucu Ayarları
        "server_title": "Sunucu Ayarları",
        "server_subtitle": "Web sitenizin dosyalarının bulunduğu klasörü ve Cloudflare Tunnel token'ınızı girin.",
        "server_folder_title": "Web Sitesi Klasörü",
        "server_folder_desc": "Statik site dosyalarınızın bulunduğu klasör (Merkez için index.html içermelidir).",
        "server_folder_secondary_desc": "Yedek düğümde dosyalar Merkez bilgisayardan bu klasöre otomatik eşitlenecektir (index.html şartı aranmaz).",
        "server_token_title": "Cloudflare Tunnel Token",
        "server_token_desc": "Cloudflare Zero Trust üzerinden oluşturduğunuz tünel token'ını girin.",
        "server_domain_title": "Site İnternet Adresi (Opsiyonel)",
        "server_domain_desc": "Cloudflare'de ayarladığınız alan adınızı girerseniz, kurulum sonrası site doğrudan internet üzerinden açılır. (Örn: https://ornek.com)",
        "server_port_title": "Yerel Caddy Portu",
        "server_port_desc": "Caddy'nin dinleyeceği yerel port. (Varsayılan: 80)",
        "server_prevent_sleep": "⚡ Bilgisayar prize takılıyken uyku moduna geçmesini engelle (7/24 HA için önerilir)",
        "server_port_ok": "✓ Port uygun",
        "server_port_caddy_reinstall": "✓ Port uygun (Mevcut Caddy servisi yenilenecek)",
        "server_port_in_use": "⚠ Port kullanımda!",
        "server_port_invalid": "Geçersiz port",

        # Sunucu Ayarları Hataları
        "err_no_folder": "Lütfen web sitesi klasörünü seçin.",
        "err_folder_not_found": "Klasör bulunamadı: {folder}",
        "err_no_index": "Seçilen klasörde index.html bulunamadı.\nBeklenen dosya: {index_path}",
        "err_no_token": "Lütfen Cloudflare Tunnel token'ını girin.",
        "err_invalid_token": "Token formatı geçersiz. Lütfen geçerli bir Cloudflare Tunnel token'ı girin. (eyJ... ile başlayan)",
        "err_port_range": "Port değeri 1-65535 arasında olmalıdır.",
        "err_port_in_use_msg": "Port {port} zaten kullanımda. Lütfen başka bir port seçin.",

        # Senkronizasyon Ayarları
        "sync_title": "Senkronizasyon (Ağ) Ayarları",
        "sync_subtitle": "Bu bilgisayarın ağdaki rolünü seçin.",
        "sync_role_title": "Bilgisayar Rolü",
        "sync_role_desc": "Bu bilgisayar ana sunucu mu olacak yoksa yedek mi?",
        "sync_role_primary": "1- Ana Bilgisayar (Merkez)",
        "sync_role_secondary": "2- Yedek Bilgisayar (Node)",
        "sync_primary_desc": "İlk kurulumu bu bilgisayarda yapıyorsanız Merkez'i seçin.",
        "sync_secondary_desc": "Bu bilgisayar Merkez ile senkronize çalışıp yedek (failover) olacaksa Yedek'i seçin.",
        "sync_join_key_title": "🔑 Hızlı Kurulum: Küme Katılım Kodu (Opsiyonel)",
        "sync_join_key_desc": "Merkez bilgisayarda üretilen 'AHWS1-...' kodunu yapıştırırsanız Cihaz ID, Cloudflare Token, Port ve Domain otomatik doldurulur!",
        "sync_join_key_applied": "✓ Küme Katılım Kodu çözümlendi! Tüm sunucu ayarları otomatik dolduruldu.",
        "sync_join_key_invalid": "⚠ Geçersiz Küme Katılım Kodu formatı.",
        "sync_device_title": "Merkez Bilgisayar ID (Syncthing Device ID)",
        "sync_device_desc": "Merkez bilgisayar kurulumu bittiğinde ekranda gösterilen ID'yi buraya yapıştırın.",

        # Senkronizasyon Hataları
        "err_no_device_id": "Lütfen Merkez Bilgisayar'ın Syncthing ID'sini veya Küme Katılım Kodunu girin.",
        "err_invalid_device_id": "Geçersiz Device ID formatı. Doğru format: AAAAAAA-BBBBBBB-...",

        # Kurulum Sayfası
        "install_title": "Kurulum Yapılıyor",
        "install_subtitle": "Lütfen bekleyin, arka planda servisler indiriliyor ve kuruluyor...",
        "install_preparing": "Kurulum hazırlanıyor...",
        "install_cancelling": "Kurulum iptal ediliyor...",
        "install_failed_status": "❌ Kurulum başarısız!",
        "install_complete_status": "✓ Kurulum tamamlandı!",

        # Bitiş Sayfası
        "finish_title": "Kurulum Tamamlandı! 🎉",
        "finish_subtitle": "Sistem başarıyla kuruldu ve arka planda çalışıyor.",
        "finish_success_msg": "Servisler (Caddy, Cloudflared, Syncthing) aktif.",
        "finish_loading": "(yükleniyor...)",
        "finish_device_id_title": "Sizin Syncthing Cihaz ID'niz:",
        "finish_device_id_desc": "Ağdaki diğer cihazların size bağlanması için bu ID gereklidir.",
        "finish_join_key_title": "🔑 Küme Katılım Kodu (Yedek Bilgisayar İçin Tek Kod):",
        "finish_join_key_desc": "Yedek bilgisayarı kurarken bu kodu yapıştırarak Token + Device ID + Port ayarlarını tek seferde aktarabilirsiniz.",
        "finish_primary_hint": "Yedek bilgisayarı (Node) kurarken bu ID'yi veya Küme Katılım Kodunu kullanın. Ardından 'Yedek Ekle' butonuyla o bilgisayarı merkeze tanıtın.",
        "finish_secondary_hint": "Yedek bilgisayar başarıyla merkeze bağlandı. Dosyalarınız otomatik olarak senkronize edilecektir.",
        "finish_open_site_desc": "Siteniz Caddy web sunucusu üzerinde yayında! Yedek düğüm eklemeden de siteniz bilgisayarınızda aktiftir.",
        "msg_copied_title": "Kopyalandı",
        "msg_copied_device_id": "Cihaz ID panoya kopyalandı.",
        "msg_copied_join_key": "Küme Katılım Kodu panoya kopyalandı.",

        # Canlı Sağlık Gösterge Paneli (Dashboard)
        "health_title": "Canlı Sistem Durumu",
        "health_running": "🟢 Çalışıyor",
        "health_stopped": "🔴 Durdu",
        "health_nodes": "Eşleşen Düğüm: {count}",

        # Hata Diyaloğu
        "error_dialog_title": "Kurulum Hatası",
        "error_dialog_desc": "Kurulum sırasında bir hata oluştu ve yapılan işlemler geri alındı.",
        "error_dialog_open_log": "📄 Log Dosyasını Aç",

        # Yedek Ekle Diyaloğu
        "node_dialog_title": "Yedek Bilgisayar (Node) Ekle",
        "node_dialog_desc": "Yedek bilgisayarda kurulum tamamlandıktan sonra ekranda çıkan Cihaz ID'sini aşağıya yapıştırın.",
        "node_dialog_local_id_title": "Ana Bilgisayar (Sizin) Cihaz ID'niz:",
        "node_dialog_input_title": "Yedek Bilgisayar ID:",
        "node_dialog_btn_add": "Ekle ve Eşleştir",
        "node_dialog_adding": "Ekleniyor...",
        "node_dialog_success": "Yedek bilgisayar başarıyla eklendi ve klasör paylaşıldı!",
        "node_dialog_error": "Hata: {error}",
        "msg_invalid_input": "Geçersiz Giriş",
        "msg_pairing": "Eşleştiriliyor... Lütfen bekleyin.",
        "msg_pairing_ok": "✓ Eşleştirme tamamlandı! Site klasörü yedek düğümle paylaşıldı.",
        "err_pairing_failed": "❌ Hata: {error}",
        "err_no_engine": "❌ Kurulum motoru bağlantısı bulunamadı.",

        # Ayarlar Diyaloğu
        "settings_title": "Sistem Ayarları",
        "settings_desc": "Değişiklikler kaydedildiğinde ilgili servisler (Caddy, Cloudflared, Syncthing) otomatik olarak güncellenir.",
        "settings_applying": "Uygulanıyor, lütfen bekleyin...",
        "settings_saved_title": "Başarılı",
        "settings_saved_msg": "Ayarlar kaydedildi ve servisler güncellendi.",
        "settings_save_failed": "Kayıt başarısız.",
        "settings_err_save": "Ayarlar uygulanırken bir hata oluştu:\n{error}",
        "uninstall_confirm_title": "Kurulumu Kaldır",
        "uninstall_confirm_msg": "Tüm AHWS servisleri (Caddy, Cloudflared, Syncthing) durdurulup kaldırılacak. Web sitesi dosyalarınız silinmez.\n\nDevam etmek istiyor musunuz?",
        "uninstall_success_msg": "Tüm servisler ve yapılandırma başarıyla kaldırıldı.",

        # Installer Engine Mesajları
        "step_caddy_dl": "Caddy indiriliyor...",
        "step_caddy_inst": "Caddy servisi kuruluyor...",
        "step_cf_dl": "Cloudflared indiriliyor...",
        "step_cf_inst": "Cloudflared servisi kuruluyor...",
        "step_sync_dl": "Syncthing indiriliyor...",
        "step_sync_inst": "Syncthing servisi kuruluyor...",
        "step_finalize": "Kurulum tamamlanıyor...",
        "step_complete": "Kurulum tamamlandı!",
        "step_cancel": "Kurulum iptal edildi.",
        "step_dirs": "Kurulum dizinleri oluşturuluyor...",
        "step_caddy": "Caddy indiriliyor ve kuruluyor...",
        "step_cf": "Cloudflared indiriliyor ve kuruluyor...",
        "step_sync": "Syncthing indiriliyor ve kuruluyor...",
        "step_device_id": "Syncthing Device ID alınıyor...",
        "step_nssm": "NSSM hazırlanıyor...",
        "step_primary": "Merkez düğüm hazırlanıyor...",
        "step_secondary": "Yedek düğüm hazırlanıyor...",
        "step_auto_accept": "Merkez cihazı eklendi ve klasör eşleştirildi...",
        "step_rollback": "Kurulum hatası, geri alma başlatılıyor...",
    },
    "en": {
        # General Buttons
        "btn_next": "Next ▶",
        "btn_back": "◀ Back",
        "btn_copy": "📋 Copy",
        "btn_browse": "📂 Browse...",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        "btn_save": "💾 Save",
        "btn_settings": "⚙️ Settings",
        "btn_refresh": "🔄 Refresh Status",
        "btn_uninstall": "🗑️ Uninstall Services",
        "btn_add_node": "➕ Add Backup Node",
        "btn_start_install": "Start Installation",
        "btn_retry": "🔄 Retry",
        "btn_go_to_manage": "🚀 Manage Setup & Add Node",
        "btn_reinstall": "⚙️ Reinstall / Fresh Setup",
        "btn_open_site": "🌐 Open Site (http://localhost)",
        "btn_open_site_browser": "🌐 Open Website in Browser",

        # Welcome
        "welcome_title": "AHWS Setup",
        "welcome_subtitle": "High Availability (HA) Static Web Setup Wizard",
        "welcome_desc": (
            "This wizard will automatically install and configure Caddy Web Server, Cloudflare Tunnel, and Syncthing services on your computer.\n\n"
            "Please ensure you have all required information (Cloudflare Token, etc.) ready before proceeding."
        ),
        "welcome_existing_title": "✓ Existing Installation Detected",
        "welcome_existing_desc": "An existing AHWS installation was detected on this machine. You can jump directly to management & node pairing without reinstalling.",
        "finish_role": "Node Role",
        "install_date_label": "Installation Date",
        "device_id_short_label": "Device ID",
        "unknown_label": "Unknown",
        "welcome_warning": "⚠ This process requires administrative privileges. Please accept the UAC prompt to continue.",

        # Server Settings
        "server_title": "Server Settings",
        "server_subtitle": "Enter your website folder path and Cloudflare Tunnel token.",
        "server_folder_title": "Website Folder",
        "server_folder_desc": "The folder containing your static site files (must include index.html for Primary).",
        "server_folder_secondary_desc": "On Secondary nodes, website files will automatically synchronize from the Primary into this folder (index.html not required beforehand).",
        "server_token_title": "Cloudflare Tunnel Token",
        "server_token_desc": "Enter the tunnel token created via Cloudflare Zero Trust.",
        "server_domain_title": "Public Website Domain (Optional)",
        "server_domain_desc": "If you enter your Cloudflare domain, the site will open directly via the internet after installation. (e.g. https://example.com)",
        "server_port_title": "Local Caddy Port",
        "server_port_desc": "The local port Caddy will listen on. (Default: 80)",
        "server_prevent_sleep": "⚡ Prevent computer from sleeping when plugged in (Recommended for 24/7 HA)",
        "server_port_ok": "✓ Port available",
        "server_port_caddy_reinstall": "✓ Port available (Existing Caddy service will be reinstalled)",
        "server_port_in_use": "⚠ Port in use!",
        "server_port_invalid": "Invalid port",

        # Server Settings Errors
        "err_no_folder": "Please select a website folder.",
        "err_folder_not_found": "Folder not found: {folder}",
        "err_no_index": "index.html not found in the selected folder.\nExpected file: {index_path}",
        "err_no_token": "Please enter your Cloudflare Tunnel token.",
        "err_invalid_token": "Invalid token format. Please enter a valid Cloudflare Tunnel token (starts with eyJ...).",
        "err_port_range": "Port value must be between 1 and 65535.",
        "err_port_in_use_msg": "Port {port} is already in use. Please select a different port.",

        # Sync Settings
        "sync_title": "Synchronization (Network) Settings",
        "sync_subtitle": "Select the role of this computer in the network.",
        "sync_role_title": "Computer Role",
        "sync_role_desc": "Will this be the primary server or the backup node?",
        "sync_role_primary": "1- Primary Computer (Center)",
        "sync_role_secondary": "2- Secondary Computer (Node)",
        "sync_primary_desc": "Select Primary if this is the first computer you are setting up.",
        "sync_secondary_desc": "Select Secondary if this computer will synchronize with Primary and act as a failover node.",
        "sync_join_key_title": "🔑 Quick Setup: Cluster Join Key (Optional)",
        "sync_join_key_desc": "Paste the 'AHWS1-...' key generated on the Primary computer to auto-fill Device ID, Cloudflare Token, Port, and Domain!",
        "sync_join_key_applied": "✓ Cluster Join Key decoded! All server settings have been auto-filled.",
        "sync_join_key_invalid": "⚠ Invalid Cluster Join Key format.",
        "sync_device_title": "Primary Computer ID (Syncthing Device ID)",
        "sync_device_desc": "Paste the Device ID shown on the Primary computer's completion screen here.",

        # Sync Errors
        "err_no_device_id": "Please enter the Primary Computer's Syncthing ID or Cluster Join Key.",
        "err_invalid_device_id": "Invalid Device ID format. Correct format: AAAAAAA-BBBBBBB-...",

        # Install Page
        "install_title": "Installing",
        "install_subtitle": "Please wait, services are being downloaded and installed in the background...",
        "install_preparing": "Preparing installation...",
        "install_cancelling": "Cancelling installation...",
        "install_failed_status": "❌ Installation failed!",
        "install_complete_status": "✓ Installation complete!",

        # Finish Page
        "finish_title": "Installation Complete! 🎉",
        "finish_subtitle": "The system has been successfully set up and is running in the background.",
        "finish_success_msg": "Services (Caddy, Cloudflared, Syncthing) are active.",
        "finish_loading": "(loading...)",
        "finish_device_id_title": "Your Syncthing Device ID:",
        "finish_device_id_desc": "This ID is required for other devices on the network to connect to you.",
        "finish_join_key_title": "🔑 Cluster Join Key (One-Key Setup for Secondary Node):",
        "finish_join_key_desc": "Paste this key when setting up a Secondary node to transfer Token + Device ID + Port settings in one click.",
        "finish_primary_hint": "Use this ID or the Cluster Join Key when setting up the Secondary computer (Node). Then use 'Add Backup Node' below to pair them.",
        "finish_secondary_hint": "The secondary computer is successfully connected to the primary. Your files will synchronize automatically.",
        "finish_open_site_desc": "Your site is live on Caddy Web Server! It is active on your computer even without adding a secondary node.",
        "msg_copied_title": "Copied",
        "msg_copied_device_id": "Device ID copied to clipboard.",
        "msg_copied_join_key": "Cluster Join Key copied to clipboard.",

        # Live Health Dashboard
        "health_title": "Live System Status",
        "health_running": "🟢 Running",
        "health_stopped": "🔴 Stopped",
        "health_nodes": "Paired Nodes: {count}",

        # Error Dialog
        "error_dialog_title": "Installation Error",
        "error_dialog_desc": "An error occurred during installation and changes have been rolled back.",
        "error_dialog_open_log": "📄 Open Log File",

        # Node Dialog
        "node_dialog_title": "Add Secondary Computer (Node)",
        "node_dialog_desc": "Paste the Device ID displayed on the secondary computer after its installation is complete.",
        "node_dialog_local_id_title": "Primary Computer (Your) Device ID:",
        "node_dialog_input_title": "Secondary Computer ID:",
        "node_dialog_btn_add": "Add and Pair",
        "node_dialog_adding": "Adding...",
        "node_dialog_success": "Secondary computer successfully added and folder shared!",
        "node_dialog_error": "Error: {error}",
        "msg_invalid_input": "Invalid Input",
        "msg_pairing": "Pairing... Please wait.",
        "msg_pairing_ok": "✓ Pairing complete! Site folder shared with the secondary node.",
        "err_pairing_failed": "❌ Error: {error}",
        "err_no_engine": "❌ Installer engine connection not found.",

        # Settings Dialog
        "settings_title": "System Settings",
        "settings_desc": "When changes are saved, related services (Caddy, Cloudflared, Syncthing) will be updated automatically.",
        "settings_applying": "Applying changes, please wait...",
        "settings_saved_title": "Success",
        "settings_saved_msg": "Settings saved and services updated.",
        "settings_save_failed": "Save failed.",
        "settings_err_save": "An error occurred while applying settings:\n{error}",
        "uninstall_confirm_title": "Uninstall Services",
        "uninstall_confirm_msg": "All AHWS services (Caddy, Cloudflared, Syncthing) will be stopped and removed. Your website files will not be deleted.\n\nDo you want to continue?",
        "uninstall_success_msg": "All services and configuration have been removed.",

        # Installer Engine Messages
        "step_caddy_dl": "Downloading Caddy...",
        "step_caddy_inst": "Installing Caddy service...",
        "step_cf_dl": "Downloading Cloudflared...",
        "step_cf_inst": "Installing Cloudflared service...",
        "step_sync_dl": "Downloading Syncthing...",
        "step_sync_inst": "Installing Syncthing service...",
        "step_finalize": "Finalizing installation...",
        "step_complete": "Installation complete!",
        "step_cancel": "Installation cancelled.",
        "step_dirs": "Creating installation directories...",
        "step_caddy": "Downloading and installing Caddy...",
        "step_cf": "Downloading and installing Cloudflared...",
        "step_sync": "Downloading and installing Syncthing...",
        "step_device_id": "Getting Syncthing Device ID...",
        "step_nssm": "Preparing NSSM...",
        "step_primary": "Preparing primary node...",
        "step_secondary": "Preparing secondary node...",
        "step_auto_accept": "Primary device added and folder paired...",
        "step_rollback": "Installation error, rolling back...",
    }
}


def set_language(lang_code: str):
    """Aktif dili değiştirir (ör. 'tr' veya 'en')."""
    global _CURRENT_LANG
    if lang_code in _TRANSLATIONS:
        _CURRENT_LANG = lang_code


def get_language() -> str:
    """Mevcut dili döndürür."""
    return _CURRENT_LANG


def t(key: str, **kwargs) -> str:
    """
    Seçili dilde anahtara karşılık gelen metni döndürür.
    Eğer keyword argument (kwargs) verilmişse .format() uygular.
    """
    text = _TRANSLATIONS.get(_CURRENT_LANG, {}).get(key)
    if text is None:
        return f"[{key}]"  # Missing translation

    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
