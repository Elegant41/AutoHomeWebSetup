# AutoHomeWebSetup

Windows kullanıcıları için **statik web siteleri** için **Basit otonom failover ağı** kuran masaüstü uygulaması.

> İleri > İleri > Kur mantığıyla çalışan, evdeki birden fazla bilgisayarı kullanarak yüksek erişilebilirlikli web sitesi altyapısı kurar.

## Özellikler

- 🖥️ **Caddy** — Hafif ve modern statik web sunucusu (`/ahws-health` uç noktası destekli)
- 🔒 **Cloudflare Tunnel** — Port açmadan dış dünyaya güvenli bağlantı
- 🔄 **Syncthing** — Bilgisayarlar arası otomatik dosya senkronizasyonu
- ⚡ **Otomatik Failover** — Cloudflare Edge, ana bilgisayar kapanırsa trafiği yedek bilgisayara yönlendirir
- 🔑 **Küme Katılım Anahtarı (`AHWS1-...`)** — Yedek bilgisayarları tek bir kod yapıştırarak saniyeler içinde kümeye dahil etme
- 🛡️ **Otomatik Güvenlik Duvarı & Güç Yönetimi** — Windows Firewall kurallarını ve uyku modu engellemesini (`powercfg`) otomatik yapılandırma
- 🩺 **Canlı Sistem Sağlık Paneli** — Servislerin çalışma durumunu ve eşleşmiş düğüm sayısını canlı izleme
- 🔄 **Tam Rollback & Kaldırıcı (Uninstaller)** — Hata veya iptal durumunda yapılan işlemleri otomatik geri alma ve tek tıkla kurulumu kaldırma

## Gereksinimler

- **Windows 10/11** (x64)
- **Python 3.10+** (geliştirme için)
- Yönetici yetkisi (kurulum sırasında otomatik istenir)
- Cloudflare hesabı ve Tunnel token'ı

## Kurulum (Geliştirme)

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
python main.py
```

## Kurulum (Dağıtım)

```bash
# PyInstaller ile derle
pyinstaller build.spec

# dist/AutoHomeWebSetup.exe dosyasını çalıştırın
```

## Kullanım

1. **Hoşgeldiniz** → Dil seçimi (TR/EN) ve İleri
2. **Senkronizasyon Ayarları** → **Merkez** veya **Yedek** rolünü seçin (Yedek ise `AHWS1-...` Katılım Anahtarını veya Merkez Device ID'sini girin)
3. **Sunucu Ayarları** → Web sitesi klasörünü seçin + Cloudflare Tunnel token'ını girin
4. **Kurulum** → Bileşenler otomatik indirilir, SHA256 doğrulaması yapılır ve Windows servisleri kurulur
5. **Bitiş & Yönetim** → Katılım Anahtarınızı / Device ID'nizi kopyalayın, canlı servis durumunu izleyin veya yedek düğüm ekleyin

### Failover Akışı

```
Kullanıcı → Cloudflare Edge → Bilgisayar A (Merkez)
                              ↓ (A kapanırsa otomatik)
                              Bilgisayar B (Yedek)
```

Her iki bilgisayar da aynı tunnel token'ı ile çalışır. Cloudflare Edge,
aktif connector'ı otomatik algılar ve kesintisiz trafik yönlendirmesi yapar.

## Antivirüs Uyarısı

> ⚠️ Bazı antivirüs programları, bu uygulamayı veya indirilen bileşenleri (Caddy, Cloudflared, Syncthing) yanlışlıkla engelleyebilir. Gerekirse antivirüsünüzde istisna ekleyin.

## Lisans

Bu proje açık kaynak bir projedir. Detaylı bilgi için lisans dosyasını inceleyin.

---

**AutoHomeWebSetup** — HA Kurulum Sihirbazı v1.0.0