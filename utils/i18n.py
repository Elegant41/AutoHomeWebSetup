"""
i18n (Internationalization) Modülü
Uygulamanın çift dil desteğini (TR/EN) sağlar.
Windows 10/11 Tkinter GDI font motoruyla %100 uyumlu semboller kullanır.
"""

_CURRENT_LANG = "tr"

_TRANSLATIONS = {
    "tr": {
        # Genel Butonlar
        "btn_next": "İleri ▶",
        "btn_back": "◀ Geri",
        "btn_copy": "Kopyala",
        "btn_copy_join_key": "Katılım Kodunu Kopyala",
        "btn_browse": "Gözat...",
        "btn_cancel": "İptal",
        "btn_close": "Kapat",
        "btn_home": "◀ Ana Ekran",
        "btn_save": "Kaydet",
        "btn_settings": "Ayarlar",
        "btn_refresh": "↻ Durumu Yenile",
        "btn_refresh_status": "↻ Durumu Yenile",
        "btn_uninstall": "Kurulumu Kaldır",
        "btn_add_node": "+ Yedek Bilgisayar Ekle",
        "btn_start_install": "Kurulumu Başlat ▶",
        "btn_retry": "↻ Tekrar Dene",
        "btn_go_to_manage": "Durum Paneli & Yedek Ekle",
        "btn_go_to_status": "Canlı Durum Paneli",
        "btn_reinstall": "Sıfırdan Yeniden Kur",
        "btn_open_site": "Siteyi Tarayıcıda Aç",
        "btn_open_site_browser": "Web Sitesini Tarayıcıda Aç",
        "btn_open_logs": "Log Dosyasını Aç",

        # Hoşgeldiniz Sayfası
        "welcome_title": "AHWS Setup",
        "welcome_subtitle": "Yüksek Erişilebilirlikli (HA) Statik Web Kurulum Sihirbazı",
        "welcome_desc": (
            "Bu sihirbaz, Caddy web sunucusu, Cloudflare Tunnel ve Syncthing servislerini otomatik olarak "
            "bilgisayarınıza kuracak ve yapılandıracaktır.\n\n"
            "İlerlemeden önce lütfen gerekli bilgilerin (Cloudflare Tunnel Token vb.) hazır olduğundan emin olun."
        ),
        "welcome_existing_title": "✓ Mevcut Kurulum Bulundu",
        "welcome_existing_desc": (
            "Bu bilgisayarda tamamlanmış bir AHWS kurulumu tespit edildi. Tekrar kurulum yapmadan doğrudan "
            "canlı durum paneline geçebilir veya ayarlarınızı yönetebilirsiniz."
        ),
        "finish_role": "Düğüm Rolü",
        "install_date_label": "Kurulum Tarihi",
        "device_id_short_label": "Cihaz ID",
        "welcome_device_id_label": "Cihaz ID",
        "unknown_label": "Bilinmiyor",
        "welcome_unknown_date": "Bilinmiyor",
        "welcome_warning": "⚠ Bu işlem yönetici hakları gerektirir. Devam etmek için UAC uyarısını onaylayın.",

        # Sunucu Ayarları Sayfası
        "server_title": "Sunucu Ayarları",
        "server_subtitle": "Web sitenizin dosyalarının bulunduğu klasörü ve Cloudflare Tunnel token'ınızı girin.",
        "server_folder_title": "Web Sitesi Klasörü",
        "server_folder_desc": "Statik site dosyalarınızın bulunduğu klasör (Merkez bilgisayar için index.html içermelidir).",
        "server_folder_secondary_desc": (
            "Yedek bilgisayarda site dosyaları Merkez bilgisayardan bu klasöre otomatik olarak eşitlenecektir "
            "(önceden index.html bulunması gerekmez)."
        ),
        "server_token_title": "Cloudflare Tunnel Token",
        "server_token_desc": "Cloudflare Zero Trust panelinden oluşturduğunuz tünel token'ını girin.",
        "server_domain_title": "Site İnternet Adresi (Opsiyonel)",
        "server_domain_desc": (
            "Cloudflare'de ayarladığınız alan adınızı girerseniz, kurulum sonrası site doğrudan bu adres üzerinden açılır "
            "(Örn: https://ornek.com)."
        ),
        "server_port_title": "Yerel Caddy Portu ve Güç Ayarı",
        "server_port_desc": "Caddy web sunucusunun dinleyeceği yerel port (Varsayılan: 80).",
        "server_prevent_sleep": "Bilgisayar prize takılıyken uyku moduna geçmesini engelle (7/24 kesintisiz erişim için önerilir)",
        "server_port_ok": "✓ Port uygun",
        "server_port_caddy_reinstall": "✓ Port uygun (Mevcut Caddy servisi güncellenecek)",
        "server_port_in_use": "⚠ Port başka bir uygulama tarafından kullanılıyor!",
        "server_port_invalid": "Geçersiz port numarası",

        # Sunucu Ayarları Hataları
        "err_no_folder": "Lütfen web sitesi klasörünü seçin.",
        "err_folder_not_found": "Klasör bulunamadı: {folder}",
        "err_no_index": "Seçilen klasörde index.html bulunamadı.\nBeklenen dosya: {index_path}",
        "err_no_token": "Lütfen Cloudflare Tunnel token'ını girin.",
        "err_invalid_token": "Token formatı geçersiz. Lütfen geçerli bir Cloudflare Tunnel token'ı girin (eyJ... ile başlayan).",
        "err_port_range": "Port değeri 1-65535 arasında olmalıdır.",
        "err_port_in_use_msg": "Port {port} zaten kullanımda. Lütfen başka bir port seçin.",

        # Senkronizasyon Ayarları Sayfası
        "sync_title": "Senkronizasyon (Ağ) Ayarları",
        "sync_subtitle": "Bu bilgisayarın yüksek erişilebilirlik (HA) ağındaki rolünü seçin.",
        "sync_role_title": "Bilgisayar Rolü",
        "sync_role_desc": "Bu bilgisayar ana sunucu mu olacak yoksa yedek düğüm mü?",
        "sync_role_primary": "1- Ana Bilgisayar (Merkez)",
        "sync_role_secondary": "2- Yedek Bilgisayar (Node)",
        "sync_primary_desc": "İlk kurulumu bu bilgisayarda yapıyorsanız ve site dosyalarınız buradaysa Merkez'i seçin.",
        "sync_secondary_desc": "Bu bilgisayar Merkez ile senkronize çalışıp yedek (failover) olacaksa Yedek'i seçin.",
        "sync_join_key_title": "Hızlı Kurulum: Küme Katılım Kodu (Opsiyonel)",
        "sync_join_key_desc": (
            "Merkez bilgisayarda üretilen 'AHWS1-...' kodunu buraya yapıştırırsanız Merkez Cihaz ID, "
            "Cloudflare Token, Port ve Domain otomatik doldurulur!"
        ),
        "sync_join_key_applied": "✓ Küme Katılım Kodu çözümlendi! Tüm sunucu ayarları otomatik dolduruldu.",
        "sync_join_key_invalid": "⚠ Geçersiz Küme Katılım Kodu formatı.",
        "err_invalid_join_key": "⚠ Geçersiz Küme Katılım Kodu formatı.",
        "sync_device_title": "Merkez Bilgisayar ID (Syncthing Device ID)",
        "sync_device_desc": "Merkez bilgisayar kurulumu bittiğinde ekranda gösterilen Cihaz ID'yi buraya yapıştırın.",

        # Senkronizasyon Hataları
        "err_no_device_id": "Lütfen Merkez Bilgisayar'ın Syncthing Cihaz ID'sini veya Küme Katılım Kodunu girin.",
        "err_invalid_device_id": "Geçersiz Device ID formatı. Doğru format: AAAAAAA-BBBBBBB-...",

        # Kurulum Sayfası
        "install_title": "Kurulum Yapılıyor",
        "install_subtitle": "Lütfen bekleyin, arka planda servisler indiriliyor ve yapılandırılıyor...",
        "install_preparing": "Kurulum hazırlanıyor...",
        "install_log_title": "Kurulum Günlüğü (Log)",
        "install_cancelling": "Kurulum iptal ediliyor...",
        "install_cancelling_log": "⚠ Kurulum iptal ediliyor, yapılan işlemler geri alınıyor...",
        "install_failed": "✕ Kurulum başarısız!",
        "install_failed_status": "✕ Kurulum başarısız!",
        "install_error_prefix": "✕ HATA: {message}",
        "install_complete": "✓ Kurulum tamamlandı!",
        "install_complete_status": "✓ Kurulum tamamlandı!",
        "install_complete_log": "✓ Kurulum başarıyla tamamlandı!",
        "install_cancelled": "⚠ Kurulum iptal edildi.",
        "install_cancelled_log": "⚠ Kurulum kullanıcı tarafından iptal edildi.",

        # Bitiş ve Durum Paneli Sayfası
        "finish_title": "Kurulum Tamamlandı!",
        "finish_subtitle": "Sistem başarıyla kuruldu ve arka planda servis olarak çalışıyor.",
        "finish_success_msg": "Servisler (Caddy, Cloudflared, Syncthing) Windows servisi olarak yapılandırıldı.",
        "finish_loading": "(yükleniyor...)",
        "finish_device_id_title": "Bu Bilgisayarın Syncthing Cihaz ID'si:",
        "finish_device_id_desc": "Yedek bilgisayarda kurulum yaptıktan sonra oradaki Cihaz ID'yi buraya ekleyin:",
        "finish_join_key_title": "Küme Katılım Kodu (AHWS1)",
        "finish_join_key_desc": "Yedek bilgisayarı tek kodla kurmak için kopyalayın (Token + ID + Port içerir).",
        "finish_primary_hint": (
            "1. Adım: Yedek bilgisayarı kurarken aşağıdaki 'Katılım Kodunu' (veya Cihaz ID'nizi) kullanın.\n"
            "2. Adım: Yedek bilgisayar kurulumu bitince, o bilgisayarın ekranda verdiği Cihaz ID'yi "
            "aşağıdaki '+ Yedek Bilgisayar Ekle' butonuyla bu bilgisayara ekleyin."
        ),
        "finish_secondary_hint": (
            "ÖNEMLİ SON ADIM: Bu bilgisayar Yedek Düğüm (Node) olarak kuruldu. Dosya eşitlemesinin başlaması için "
            "yukarıdaki Cihaz ID'nizi kopyalayın ve ANA (Merkez) bilgisayardaki AHWS programında "
            "'+ Yedek Bilgisayar Ekle' butonuna basarak bu ID'yi ekleyin!"
        ),
        "finish_open_site_desc": "Web siteniz Caddy üzerinde yayında! Aşağıdaki butonlarla sitenizi açabilir veya ayarları değiştirebilirsiniz.",
        "msg_copied_title": "Kopyalandı",
        "msg_copied_device_id": "Cihaz ID panoya kopyalandı.",
        "msg_copied_join_key": "Küme Katılım Kodu panoya kopyalandı.",

        # Canlı Sağlık Gösterge Paneli (Dashboard)
        "health_title": "Canlı Sistem ve Servis Durumu",
        "health_card_title": "Canlı Sistem ve Servis Durumu",
        "health_col_caddy": "Caddy (Web Sunucu)",
        "health_col_cloudflared": "Cloudflared (Tünel)",
        "health_col_syncthing": "Syncthing (Senkron)",
        "health_col_nodes": "Senkronizasyon Ağı",
        "health_running": "● Çalışıyor",
        "health_stopped": "● Durdu",
        "health_nodes": "● {count} Düğüm Ekli",
        "health_paired_nodes": "● {count} Düğüm Ekli",
        "health_nodes_connected": "● {connected}/{total} Cihaz Bağlı",
        "health_nodes_waiting": "● {total} Ekli (Bağlantı Bekleniyor)",
        "health_nodes_none": "● Eşleşen Cihaz Yok",

        # Hata Diyaloğu
        "error_dialog_title": "Kurulum Hatası",
        "error_dialog_desc": "Kurulum sırasında bir hata oluştu ve yapılan işlemler geri alındı.",
        "error_dialog_open_log": "Log Dosyasını Aç",

        # Yedek Ekle Diyaloğu
        "node_dialog_title": "Yedek Bilgisayar (Node) Ekle",
        "node_dialog_desc": (
            "Yedek bilgisayarda kurulum tamamlandığında ekranda gösterilen Syncthing Cihaz ID'sini "
            "aşağıdaki alana yapıştırıp 'Ekle ve Eşleştir' butonuna tıklayın."
        ),
        "node_dialog_local_id_title": "Ana Bilgisayar (Sizin) Cihaz ID'niz:",
        "node_dialog_input_title": "Eklenecek Yedek Bilgisayarın Cihaz ID'si:",
        "node_dialog_btn_add": "Ekle ve Eşleştir",
        "node_dialog_adding": "Ekleniyor...",
        "node_dialog_success": "Yedek bilgisayar başarıyla eklendi ve klasör paylaşıldı!",
        "node_dialog_error": "Hata: {error}",
        "msg_invalid_input": "Geçersiz Giriş",
        "msg_pairing": "Eşleştiriliyor... Lütfen bekleyin.",
        "msg_pairing_ok": "✓ Eşleştirme tamamlandı! Site klasörü yedek düğümle paylaşıldı.",
        "err_pairing_failed": "✕ Hata: {error}",
        "err_no_engine": "✕ Kurulum motoru bağlantısı bulunamadı.",

        # Ayarlar Diyaloğu
        "settings_title": "Sistem Ayarları",
        "settings_header": "Sistem Ayarları",
        "settings_desc": "Değişiklikler kaydedildiğinde ilgili servisler (Caddy, Cloudflared, Syncthing) otomatik olarak güncellenir.",
        "settings_applying": "Uygulanıyor, lütfen bekleyin...",
        "settings_saved_title": "Başarılı",
        "settings_saved_msg": "Ayarlar kaydedildi ve servisler güncellendi.",
        "settings_save_failed": "Kayıt başarısız.",
        "settings_error_title": "Hata",
        "settings_err_save": "Ayarlar uygulanırken bir hata oluştu:\n{error}",
        "settings_error_msg": "Ayarlar uygulanırken bir hata oluştu:\n{error}",
        "uninstall_confirm_title": "Kurulumu Kaldır",
        "uninstall_confirm_msg": (
            "Tüm AHWS servisleri (Caddy, Cloudflared, Syncthing) durdurulup kaldırılacak. "
            "Web sitesi dosyalarınız silinmez.\n\nDevam etmek istiyor musunuz?"
        ),
        "uninstall_success_title": "Kaldırıldı",
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
        "step_nssm": "NSSM servis yöneticisi hazırlanıyor...",
        "step_primary": "Merkez düğüm hazırlanıyor...",
        "step_secondary": "Yedek düğüm hazırlanıyor...",
        "step_auto_accept": "Merkez cihazı eklendi ve klasör eşleştirildi...",
        "step_rollback": "Kurulum hatası, yapılan işlemler geri alınıyor...",

        # Modern Sihirbaz Üst Bar & Özellik Kartları
        "step_nav_1": "1. Başlangıç",
        "step_nav_2": "2. Rol & Eşleşme",
        "step_nav_3": "3. Sunucu & Tünel",
        "step_nav_4": "4. Kurulum",
        "step_nav_5": "5. Durum Paneli",
        "feat_1_title": "● Otonom Failover",
        "feat_1_desc": "Ana bilgisayar kapansa bile Cloudflare Tunnel trafiği kesintisiz yedek bilgisayara aktarır.",
        "feat_2_title": "↻ Anlık Senkronizasyon",
        "feat_2_desc": "Syncthing ile site dosyalarınız tüm bilgisayarlar arasında şifreli ve otomatik eşitlenir.",
        "feat_3_title": "✓ Sıfır Karmaşa",
        "feat_3_desc": "Docker veya K8s gerektirmeden doğrudan Windows Servisi olarak arka planda çalışır.",
        "btn_paste": "Yapıştır",
        "btn_show": "Göster",
        "btn_hide": "Gizle",
        "btn_copied_inline": "✓ Kopyalandı",
        "btn_open_syncthing": "Syncthing Paneli",
        "sync_device_valid": "✓ Geçerli Syncthing Cihaz Kimliği formatı",
        "sync_device_invalid_live": "⚠ Cihaz Kimliği 8 bloklu (56 karakter + 7 tire) olmalıdır",
        "server_folder_valid": "✓ Klasör doğrulandı (index.html mevcut)",
        "server_folder_no_index_live": "⚠ Seçilen klasörde index.html bulunamadı",
        "server_folder_ready_secondary": "✓ Yedek düğüm senkronizasyon klasörü hazır",
        "err_self_device_id": "Kendi bilgisayarınızın Cihaz ID'sini girdiniz. Lütfen YEDEK bilgisayarın Cihaz ID'sini girin.",
        "stage_nssm": "1. NSSM",
        "stage_caddy": "2. Caddy",
        "stage_cloudflared": "3. Cloudflared",
        "stage_syncthing": "4. Syncthing",
        "stage_firewall": "5. Güvenlik Duvarı",
    },
    "en": {
        # General Buttons
        "btn_next": "Next ▶",
        "btn_back": "◀ Back",
        "btn_copy": "Copy",
        "btn_copy_join_key": "Copy Join Key",
        "btn_browse": "Browse...",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        "btn_home": "◀ Home",
        "btn_save": "Save",
        "btn_settings": "Settings",
        "btn_refresh": "↻ Refresh Status",
        "btn_refresh_status": "↻ Refresh Status",
        "btn_uninstall": "Uninstall Services",
        "btn_add_node": "+ Add Secondary Node",
        "btn_start_install": "Start Installation ▶",
        "btn_retry": "↻ Retry",
        "btn_go_to_manage": "Status Panel & Add Node",
        "btn_go_to_status": "Live Status Panel",
        "btn_reinstall": "Reinstall / Fresh Setup",
        "btn_open_site": "Open Site in Browser",
        "btn_open_site_browser": "Open Website in Browser",
        "btn_open_logs": "Open Log File",

        # Welcome Page
        "welcome_title": "AHWS Setup",
        "welcome_subtitle": "High Availability (HA) Static Web Setup Wizard",
        "welcome_desc": (
            "This wizard will automatically install and configure Caddy Web Server, Cloudflare Tunnel, "
            "and Syncthing services on your computer.\n\n"
            "Please ensure you have all required information (Cloudflare Tunnel Token, etc.) ready before proceeding."
        ),
        "welcome_existing_title": "✓ Existing Installation Detected",
        "welcome_existing_desc": (
            "An existing AHWS installation was detected on this computer. You can jump directly to the live "
            "status panel or manage your settings without reinstalling."
        ),
        "finish_role": "Node Role",
        "install_date_label": "Installation Date",
        "device_id_short_label": "Device ID",
        "welcome_device_id_label": "Device ID",
        "unknown_label": "Unknown",
        "welcome_unknown_date": "Unknown",
        "welcome_warning": "⚠ This process requires administrative privileges. Please accept the UAC prompt to continue.",

        # Server Settings Page
        "server_title": "Server Settings",
        "server_subtitle": "Enter your website folder path and Cloudflare Tunnel token.",
        "server_folder_title": "Website Folder",
        "server_folder_desc": "The folder containing your static site files (must include index.html for Primary).",
        "server_folder_secondary_desc": (
            "On Secondary nodes, website files will automatically synchronize from the Primary into this folder "
            "(index.html is not required beforehand)."
        ),
        "server_token_title": "Cloudflare Tunnel Token",
        "server_token_desc": "Enter the tunnel token created via Cloudflare Zero Trust.",
        "server_domain_title": "Public Website Domain (Optional)",
        "server_domain_desc": (
            "If you enter your Cloudflare domain, the site will open directly via this URL after installation "
            "(e.g. https://example.com)."
        ),
        "server_port_title": "Local Caddy Port & Power Settings",
        "server_port_desc": "The local port Caddy will listen on (Default: 80).",
        "server_prevent_sleep": "Prevent computer from sleeping when plugged into AC power (Recommended for 24/7 HA)",
        "server_port_ok": "✓ Port available",
        "server_port_caddy_reinstall": "✓ Port available (Existing Caddy service will be updated)",
        "server_port_in_use": "⚠ Port is in use by another application!",
        "server_port_invalid": "Invalid port number",

        # Server Settings Errors
        "err_no_folder": "Please select a website folder.",
        "err_folder_not_found": "Folder not found: {folder}",
        "err_no_index": "index.html not found in the selected folder.\nExpected file: {index_path}",
        "err_no_token": "Please enter your Cloudflare Tunnel token.",
        "err_invalid_token": "Invalid token format. Please enter a valid Cloudflare Tunnel token (starts with eyJ...).",
        "err_port_range": "Port value must be between 1 and 65535.",
        "err_port_in_use_msg": "Port {port} is already in use. Please select a different port.",

        # Sync Settings Page
        "sync_title": "Synchronization (Network) Settings",
        "sync_subtitle": "Select the role of this computer in the High Availability (HA) network.",
        "sync_role_title": "Computer Role",
        "sync_role_desc": "Will this be the primary server or a secondary backup node?",
        "sync_role_primary": "1- Primary Computer (Center)",
        "sync_role_secondary": "2- Secondary Computer (Node)",
        "sync_primary_desc": "Select Primary if this is the first computer you are setting up and holds your site files.",
        "sync_secondary_desc": "Select Secondary if this computer will synchronize with Primary and act as a failover node.",
        "sync_join_key_title": "Quick Setup: Cluster Join Key (Optional)",
        "sync_join_key_desc": (
            "Paste the 'AHWS1-...' key generated on the Primary computer to auto-fill Primary Device ID, "
            "Cloudflare Token, Port, and Domain!"
        ),
        "sync_join_key_applied": "✓ Cluster Join Key decoded! All server settings have been auto-filled.",
        "sync_join_key_invalid": "⚠ Invalid Cluster Join Key format.",
        "err_invalid_join_key": "⚠ Invalid Cluster Join Key format.",
        "sync_device_title": "Primary Computer ID (Syncthing Device ID)",
        "sync_device_desc": "Paste the Device ID shown on the Primary computer's completion screen here.",

        # Sync Errors
        "err_no_device_id": "Please enter the Primary Computer's Syncthing Device ID or Cluster Join Key.",
        "err_invalid_device_id": "Invalid Device ID format. Correct format: AAAAAAA-BBBBBBB-...",

        # Install Page
        "install_title": "Installing",
        "install_subtitle": "Please wait, services are being downloaded and configured in the background...",
        "install_preparing": "Preparing installation...",
        "install_log_title": "Installation Log",
        "install_cancelling": "Cancelling installation...",
        "install_cancelling_log": "⚠ Cancelling installation and rolling back changes...",
        "install_failed": "✕ Installation failed!",
        "install_failed_status": "✕ Installation failed!",
        "install_error_prefix": "✕ ERROR: {message}",
        "install_complete": "✓ Installation complete!",
        "install_complete_status": "✓ Installation complete!",
        "install_complete_log": "✓ Installation completed successfully!",
        "install_cancelled": "⚠ Installation cancelled.",
        "install_cancelled_log": "⚠ Installation was cancelled by the user.",

        # Finish & Status Panel Page
        "finish_title": "Installation Complete!",
        "finish_subtitle": "The system has been successfully set up and is running as background services.",
        "finish_success_msg": "Services (Caddy, Cloudflared, Syncthing) are configured as Windows services.",
        "finish_loading": "(loading...)",
        "finish_device_id_title": "This Computer's Syncthing Device ID:",
        "finish_device_id_desc": "After installing on a Secondary computer, add its Device ID here:",
        "finish_join_key_title": "Cluster Join Key (AHWS1)",
        "finish_join_key_desc": "Copy this key for one-paste setup on Secondary nodes (includes Token + ID + Port).",
        "finish_primary_hint": (
            "Step 1: Use the 'Cluster Join Key' below (or your Device ID) when installing on the Secondary computer.\n"
            "Step 2: Once the Secondary computer finishes setup, copy its Device ID and add it here via '+ Add Secondary Node'."
        ),
        "finish_secondary_hint": (
            "IMPORTANT FINAL STEP: This computer is set up as a Secondary Node. To start file synchronization, "
            "copy your Device ID above and add it on the PRIMARY computer using the '+ Add Secondary Node' button!"
        ),
        "finish_open_site_desc": "Your website is live on Caddy Web Server! Use the buttons below to open your site or adjust settings.",
        "msg_copied_title": "Copied",
        "msg_copied_device_id": "Device ID copied to clipboard.",
        "msg_copied_join_key": "Cluster Join Key copied to clipboard.",

        # Live Health Dashboard
        "health_title": "Live System & Service Status",
        "health_card_title": "Live System & Service Status",
        "health_col_caddy": "Caddy (Web Server)",
        "health_col_cloudflared": "Cloudflared (Tunnel)",
        "health_col_syncthing": "Syncthing (Sync)",
        "health_col_nodes": "Sync Cluster",
        "health_running": "● Running",
        "health_stopped": "● Stopped",
        "health_nodes": "● {count} Nodes Added",
        "health_paired_nodes": "● {count} Nodes Added",
        "health_nodes_connected": "● {connected}/{total} Connected",
        "health_nodes_waiting": "● {total} Added (Waiting)",
        "health_nodes_none": "● No Paired Nodes",

        # Error Dialog
        "error_dialog_title": "Installation Error",
        "error_dialog_desc": "An error occurred during installation and changes have been rolled back.",
        "error_dialog_open_log": "Open Log File",

        # Node Dialog
        "node_dialog_title": "Add Secondary Computer (Node)",
        "node_dialog_desc": (
            "Paste the Syncthing Device ID displayed on the Secondary computer after its installation is complete, "
            "then click 'Add and Pair'."
        ),
        "node_dialog_local_id_title": "Primary Computer (Your) Device ID:",
        "node_dialog_input_title": "Secondary Computer's Device ID to Add:",
        "node_dialog_btn_add": "Add and Pair",
        "node_dialog_adding": "Adding...",
        "node_dialog_success": "Secondary computer successfully added and folder shared!",
        "node_dialog_error": "Error: {error}",
        "msg_invalid_input": "Invalid Input",
        "msg_pairing": "Pairing... Please wait.",
        "msg_pairing_ok": "✓ Pairing complete! Site folder shared with the secondary node.",
        "err_pairing_failed": "✕ Error: {error}",
        "err_no_engine": "✕ Installer engine connection not found.",

        # Settings Dialog
        "settings_title": "System Settings",
        "settings_header": "System Settings",
        "settings_desc": "When changes are saved, related services (Caddy, Cloudflared, Syncthing) will be updated automatically.",
        "settings_applying": "Applying changes, please wait...",
        "settings_saved_title": "Success",
        "settings_saved_msg": "Settings saved and services updated.",
        "settings_save_failed": "Save failed.",
        "settings_error_title": "Error",
        "settings_err_save": "An error occurred while applying settings:\n{error}",
        "settings_error_msg": "An error occurred while applying settings:\n{error}",
        "uninstall_confirm_title": "Uninstall Services",
        "uninstall_confirm_msg": (
            "All AHWS services (Caddy, Cloudflared, Syncthing) will be stopped and removed. "
            "Your website files will not be deleted.\n\nDo you want to continue?"
        ),
        "uninstall_success_title": "Uninstalled",
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
        "step_nssm": "Preparing NSSM service manager...",
        "step_primary": "Preparing primary node...",
        "step_secondary": "Preparing secondary node...",
        "step_auto_accept": "Primary device added and folder paired...",
        "step_rollback": "Installation error, rolling back changes...",

        # Modern Wizard Top Bar & Feature Cards
        "step_nav_1": "1. Welcome",
        "step_nav_2": "2. Role & Sync",
        "step_nav_3": "3. Server & Tunnel",
        "step_nav_4": "4. Install",
        "step_nav_5": "5. Dashboard",
        "feat_1_title": "● Autonomous Failover",
        "feat_1_desc": "Cloudflare Tunnel routes traffic to the backup node immediately if primary goes offline.",
        "feat_2_title": "↻ Instant Sync",
        "feat_2_desc": "Site files are automatically synced across all nodes via Syncthing.",
        "feat_3_title": "✓ Zero Complexity",
        "feat_3_desc": "Runs natively as Windows Services in the background without K8s or Docker.",
        "btn_paste": "Paste",
        "btn_show": "Show",
        "btn_hide": "Hide",
        "btn_copied_inline": "✓ Copied",
        "btn_open_syncthing": "Syncthing UI",
        "sync_device_valid": "✓ Valid Syncthing Device ID format",
        "sync_device_invalid_live": "⚠ Device ID must have 8 blocks (56 chars + 7 dashes)",
        "server_folder_valid": "✓ Folder verified (index.html found)",
        "server_folder_no_index_live": "⚠ index.html not found in selected folder",
        "server_folder_ready_secondary": "✓ Secondary node sync folder ready",
        "err_self_device_id": "You entered this computer's own Device ID. Please enter the SECONDARY computer's Device ID.",
        "stage_nssm": "1. NSSM",
        "stage_caddy": "2. Caddy",
        "stage_cloudflared": "3. Cloudflared",
        "stage_syncthing": "4. Syncthing",
        "stage_firewall": "5. Firewall",
    },
}

TRANSLATIONS = _TRANSLATIONS


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
