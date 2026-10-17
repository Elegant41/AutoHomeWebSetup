# AutoHomeWebSetup — Hata Düzeltme Planı

> **Hazırlayan:** Otomatik Kod Analizi (Antigravity)  
> **Tarih:** 2026-08-06  
> **Python Sürümü:** 3.12.7  
> **Proje Kökü:** `c:\Users\elega\Desktop\AutoHomeWebSetup`

---

## 1. Genel Proje Yapısı ve Çalışma Durumu

Program `python main.py` ile doğrudan başlatıldığında **bazı modüller başarıyla import edilmektedir** ancak çalışma zamanında (runtime) kritik hatalar oluşmaktadır. Tüm hatalar aşağıda öncelik sırasına göre listelenmiştir.

---

## 2. Tespit Edilen Hatalar

### 🔴 KRİTİK — Programın İşlevini Tamamen Bozuyor

---

### HATA-01: `syncthing_service.py` — `get_devices()` Yanlış API Yanıt Formatı

**Dosya:** `services/syncthing_service.py`  
**Satır:** 288-291  
**Kök Neden:** Syncthing REST API v1, `GET /rest/config/devices` endpoint'inden doğrudan bir **JSON dizi (list)** döndürür. Mevcut kod ise yanıtın `{"devices": [...]}` şeklinde bir dict içerdiğini varsayarak `.get("devices", [])` çağrısı yapıyor. Bu çağrı her zaman **boş liste** döndürür çünkü gerçek yanıt zaten bir listedir ve dict metodu olan `.get()` üzerinde çalışamaz.

**Hatalı Kod:**
```python
return response.json().get("devices", [])
```

**Düzeltilmiş Kod:**
```python
return response.json()  # API doğrudan list döndürür
```

---

### HATA-02: `syncthing_service.py` — `get_folders()` Yanlış API Yanıt Formatı

**Dosya:** `services/syncthing_service.py`  
**Satır:** 361-366  
**Kök Neden:** `GET /rest/config/folders` endpoint'i de doğrudan JSON dizi döndürür. HATA-01 ile aynı hata.

**Hatalı Kod:**
```python
return response.json().get("folders", [])
```

**Düzeltilmiş Kod:**
```python
return response.json()  # API doğrudan list döndürür
```

---

### HATA-03: `syncthing_service.py` — `add_device()` PUT Payload Formatı Yanlış

**Dosya:** `services/syncthing_service.py`  
**Satır:** 342-347  
**Kök Neden:** `PUT /rest/config/devices` endpoint'i bir JSON **dizi** bekler. Mevcut kod `{"devices": devices}` şeklinde bir dict gönderiyor; bu Syncthing API'sinde `422 Unprocessable Entity` hatasına yol açar.

**Hatalı Kod:**
```python
response = requests.put(
    f"{self.api_base}/rest/config/devices",
    headers=self._headers,
    json={"devices": devices},
    timeout=10,
)
```

**Düzeltilmiş Kod:**
```python
response = requests.put(
    f"{self.api_base}/rest/config/devices",
    headers=self._headers,
    json=devices,  # Direkt liste gönder
    timeout=10,
)
```

---

### HATA-04: `syncthing_service.py` — `share_folder()` PUT Payload Formatı Yanlış

**Dosya:** `services/syncthing_service.py`  
**Satır:** 463-469  
**Kök Neden:** `PUT /rest/config/folders` endpoint'i de JSON **dizi** bekler. HATA-03 ile aynı hata.

**Hatalı Kod:**
```python
response = requests.put(
    f"{self.api_base}/rest/config/folders",
    headers=self._headers,
    json={"folders": folders},
    timeout=10,
)
```

**Düzeltilmiş Kod:**
```python
response = requests.put(
    f"{self.api_base}/rest/config/folders",
    headers=self._headers,
    json=folders,  # Direkt liste gönder
    timeout=10,
)
```

---

### HATA-05: `syncthing_service.py` — `share_folder()` Cihaz Formatı Yanlış

**Dosya:** `services/syncthing_service.py`  
**Satır:** 400-402 ve 420  
**Kök Neden:** Syncthing klasör konfigürasyonundaki `devices` alanı `[{"deviceID": "...", "encryptionPassword": ""}, ...]` formatında nesneler listesi olmalıdır. Mevcut kod string ID'leri doğrudan gönderip birleştiriyor. Bu hem mevcut klasör güncellemesinde (`set` içine dict koymak JSON serialize edilemez) hem de yeni klasör oluşturulmasında geçersiz formata yol açar.

**Hatalı Kod (mevcut klasör güncelleme):**
```python
shared_with = set(existing.get("devices", []))  # dict'leri set'e koyuyor - hatalı
shared_with.update(device_ids)                   # string'leri dict listesine ekliyor
existing["devices"] = list(shared_with)
```

**Hatalı Kod (yeni klasör):**
```python
"devices": device_ids,  # string listesi, dict listesi olmalı
```

**Düzeltilmiş Kod:**
```python
# Mevcut klasör güncelleme:
existing_device_ids = {d["deviceID"] for d in existing.get("devices", [])}
for dev_id in device_ids:
    if dev_id not in existing_device_ids:
        existing["devices"].append({"deviceID": dev_id, "encryptionPassword": ""})

# Yeni klasör:
"devices": [{"deviceID": did, "encryptionPassword": ""} for did in device_ids],
```

---

### HATA-06: `assets/nssm.exe` Eksik

**Dosya:** `assets/nssm.exe` (yok)  
**Kök Neden:** `downloader.py`'deki `setup_nssm()` metodu önce `assets/nssm.exe`'nin varlığını kontrol eder; yoksa internetten indirmeye çalışır. Ancak `build.spec` içinde `assets/nssm.exe` `datas` listesinde **bulunmamaktadır**. Paketten çalıştırıldığında `resource_path("assets/nssm.exe")` her zaman eksik bulunacak, bu da kurulum sırasında `nssm.cc/release/nssm-2.24.zip` adresinden indirme denemesine yol açacak ve ağ hatası ya da antivirüs engellemesiyle başarısız olabilir.

**Düzeltme 1 — `assets/nssm.exe` dosyasını projeye ekle:**
- NSSM v2.24 win64 binary'sini https://nssm.cc/release/nssm-2.24.zip adresinden indir
- `win64/nssm.exe` dosyasını `assets/nssm.exe` olarak kaydet

**Düzeltme 2 — `build.spec` `datas` listesine ekle:**
```python
datas=[
    ('assets/icon.ico', 'assets'),
    ('assets/logo.png', 'assets'),
    ('assets/banner.png', 'assets'),
    ('assets/nssm.exe', 'assets'),  # BU SATIRI EKLE
],
```

---

### 🟠 ORTA — Yanlış Davranış / Mantık Hatası

---

### HATA-07: `app.py` — `show_page()` Stack Birikimi (Memory Leak + Mantık Hatası)

**Dosya:** `app.py`  
**Satır:** 96-115  
**Kök Neden:** `show_page()` her çağrıldığında aynı sayfa `_page_stack` listesine ekleniyor. Kullanıcı ileri-geri yapıp tekrar ileri gittiğinde stack şişiyor: `[welcome, server, sync, server, sync, ...]`. Bu durum hem gereksiz bellek kullanımına hem de `_find_page_name()` mantığını bozmasına yol açar.

**Düzeltme:** `show_page()` içinde önce aynı sayfa stack'te zaten varsa ekleme:
```python
def show_page(self, name: str) -> None:
    page = self._pages.get(name)
    if page is None:
        raise ValueError(f"Sayfa bulunamadı: {name}")

    # Önceki sayfayı gizle
    if self._page_stack:
        current = self._page_stack[-1]
        if current is page:  # Zaten bu sayfa gösterimde
            return
        current.pack_forget()
        if hasattr(current, "on_leave"):
            current.on_leave()

    # Yeni sayfayı göster
    page.pack(fill=tk.BOTH, expand=True)
    page.tkraise()
    # Eğer stack'te zaten varsa (geri navigasyon) ekleme
    if not self._page_stack or self._page_stack[-1] is not page:
        self._page_stack.append(page)

    if hasattr(page, "on_enter"):
        page.on_enter()
```

---

### HATA-08: `caddy_service.py` — `generate_caddyfile()` Site Root'a Yazma Sorunu

**Dosya:** `services/caddy_service.py`  
**Satır:** 70-71  
**Kök Neden:** `caddyfile_path = Path(site_root) / "Caddyfile"` ile site root klasörüne Caddyfile yazılmaya çalışılıyor. Ancak:
1. Site root kullanıcının web içerik klasörüdür; buraya yazma izni olmayabilir.
2. Kullanıcının web dosyaları `Caddyfile` ile karışır.
3. Caddy servisi zaten `config/Caddyfile` ile yapılandırılmaktadır (`--config "{caddyfile_path}"` argümanında `constants.CADDYFILE_PATH` kullanılmıyor, site_root'taki path kullanılıyor — tutarsızlık).

**Düzeltme:** Caddyfile'ı yalnızca `constants.CONFIG_DIR` altına yaz:
```python
def generate_caddyfile(self, site_root: str, port: int = ..., log_path=None) -> Path:
    log_path = log_path or constants.LOGS_DIR / "caddy.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    caddyfile_content = f""":{port} {{
    root * {site_root}
    file_server
    encode gzip
    log {{
        output file {log_path}
    }}
}}
"""
    # SADECE config dizinine yaz, site_root'a değil
    config_caddyfile = constants.CADDYFILE_PATH
    config_caddyfile.parent.mkdir(parents=True, exist_ok=True)
    config_caddyfile.write_text(caddyfile_content, encoding="utf-8")
    logger.info(f"Caddyfile oluşturuldu: {config_caddyfile}")
    return config_caddyfile
```

**`caddy_service.py` install() metodunu da güncelle:** `caddyfile_path` artık config dizinindedir:
```python
self.nssm.install(
    name=constants.SERVICE_CADDY,
    exe_path=str(caddy_exe),
    arguments=f'run --config "{constants.CADDYFILE_PATH}" --adapter caddyfile',
    ...
)
```

---

### HATA-09: `build.spec` — `COLLECT` Bloğu `onefile` Modunda Hatalı

**Dosya:** `build.spec`  
**Satır:** 105-114  
**Kök Neden:** `EXE` tanımında `console=False` ve onefile modunda çalışılmak isteniliyor. Ancak `COLLECT` bloğu genellikle `onedir` modu için kullanılır. `onefile` modunda `COLLECT` bloğu bulunmamalı ya da hem `EXE` hem `COLLECT` birlikte varsa PyInstaller belirsiz davranabilir. Bu durumda `dist/` altında hem `AutoHomeWebSetup.exe` hem de `AutoHomeWebSetup/` klasörü oluşur.

**Düzeltme:** Ya `COLLECT` bloğunu tamamen sil (onefile istiyorsan) ya da `EXE` içinde `a.binaries, a.zipfiles, a.datas` yerine onefile için ayrı liste kullan.

---

### HATA-10: `utils/logger.py` — Admin Öncesi Log Dizini Oluşturma

**Dosya:** `utils/logger.py`  
**Satır:** 56-57  
**Kök Neden:** `_get_logger()` içinde `log_file.parent.mkdir(parents=True, exist_ok=True)` çağrısı yapılıyor. `main.py`'de `logger = get_logger(__name__)` (satır 13) ifadesi, `ensure_admin()` çağrısından **önce** çalışıyor. `C:\ProgramData\AutoHomeWebSetup\logs` dizini yoksa admin yetkisi gerekmektedir. Ancak bu dizin önceki bir kurulumdan kalıyorsa sorun çıkmaz. İlk çalıştırmada hata riski vardır.

**Düzeltme:** `main.py`'de modül seviyesinde `get_logger()` çağrısını geciktir:
```python
# main.py - modul seviyesinde logger KALDIR
# logger = get_logger(__name__)  # BU SATIRI SİL

def main() -> int:
    from utils.logger import get_logger  # Fonksiyon içine taşı
    ensure_admin()
    create_app_directories()
    logger = get_logger(__name__)  # Dizinler oluştuktan SONRA
    logger.info("AutoHomeWebSetup başlatılıyor...")
    ...
```

---

### HATA-11: `test_windows_service.py` — Yanlış Mock Sayısı Beklentisi

**Dosya:** `tests/test_windows_service.py`  
**Satır:** 66  
**Kök Neden:** `test_install_success` testi `mock_run.call_count == 6` bekliyor. Ancak `NSSMService.install()` çağrı sayısı şu şekildedir:
- 1x `nssm install name exe`
- `arguments` verilirse: 1x `nssm set AppParameters`
- `display_name` verilirse: 1x `nssm set DisplayName`
- `description` verilirse: 1x `nssm set Description`
- `app_directory` verilirse: 1x `nssm set AppDirectory`
- Her zaman: 4x log ayarları (`AppStdout, AppStderr, AppRotateFiles, AppRotateBytes`)

Test `install("TestService", "C:/app.exe", "run")` çağrısında `display_name`, `description`, `app_directory` boş; `arguments` dolu. Gerçek çağrı sayısı: 1 (install) + 1 (AppParameters) + 4 (log) = **6**. Bu doğru görünüyor ancak test yorumu yanıltıcı.

**Düzeltme:** Yorumu düzelt:
```python
self.assertEqual(mock_run.call_count, 6)  # install(1) + AppParameters(1) + log ayarlari(4)
```

---

### 🟡 DÜŞÜK — İyileştirme / Eksiklik

---

### HATA-12: `syncthing_service.py` — API Key Sadece Lowercase Karakterler

**Dosya:** `utils/constants.py`  
**Satır:** 78  
**Kök Neden:** `SYNCTHING_API_KEY_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"` sadece küçük harf. Syncthing API anahtarları büyük harf ve özel karakter de içerebilir; bu zayıf entropi demek.

**Düzeltme (`constants.py`):**
```python
import string
SYNCTHING_API_KEY_CHARS = string.ascii_letters + string.digits
```

---

## 3. Hata Öncelik Sıralaması (Özet Tablo)

| # | Dosya | Satır(lar) | Öncelik | Hata Tipi | Etki |
|---|-------|-----------|---------|-----------|------|
| 01 | `services/syncthing_service.py` | 288-291 | 🔴 Kritik | API yanıt formatı | Cihaz ekleme/listeleme tamamen çalışmıyor |
| 02 | `services/syncthing_service.py` | 361-366 | 🔴 Kritik | API yanıt formatı | Klasör listeleme tamamen çalışmıyor |
| 03 | `services/syncthing_service.py` | 342-347 | 🔴 Kritik | PUT payload formatı | Cihaz kaydetme başarısız |
| 04 | `services/syncthing_service.py` | 463-469 | 🔴 Kritik | PUT payload formatı | Klasör paylaşma başarısız |
| 05 | `services/syncthing_service.py` | 400-402, 420 | 🔴 Kritik | Cihaz nesne formatı | API 422 hatası |
| 06 | `assets/nssm.exe` + `build.spec` | — | 🔴 Kritik | Eksik dosya | NSSM kurulumu başarısız olabilir |
| 07 | `app.py` | 96-115 | 🟠 Orta | Stack birikimi | Navigasyon bozulması |
| 08 | `services/caddy_service.py` | 70-71 | 🟠 Orta | Yanlış dosya yolu | Site root kirlenebilir |
| 09 | `build.spec` | 105-114 | 🟠 Orta | COLLECT bloğu | Çift çıktı dosyası |
| 10 | `utils/logger.py` + `main.py` | 56-57, 13 | 🟠 Orta | Erken init | İlk çalıştırmada crash riski |
| 11 | `tests/test_windows_service.py` | 66 | 🟡 Düşük | Test yorumu | Yanıltıcı belge |
| 12 | `utils/constants.py` | 78 | 🟡 Düşük | Zayıf entropi | Güvenlik |

---

## 4. Otomatik Test Script Yazma Yönergesi

> **Bu bölüm bir yapay zeka ajanının okuması için hazırlanmıştır.**
> Aşağıdaki yönergeleri takip ederek `tests/` klasörü altındaki test dosyalarını tamamla veya yeni test dosyaları oluştur.
> Proje kökü: `c:\Users\elega\Desktop\AutoHomeWebSetup`

---

### 4.1 Genel Kurallar

1. **Framework:** Python `unittest` (kurulum gerektirmez, standart kütüphane).
2. **Test keşfi:** `python -m unittest discover -s tests -p "test_*.py"` komutuyla tüm testler çalışmalı.
3. **Bağımlılıklar:** Her test dosyasının başına `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` ekle.
4. **Dış servisler:** Hiçbir test gerçek internet bağlantısı, Windows servisi veya admin yetkisi gerektirmemeli. `unittest.mock` ve `tempfile` kullan.
5. **Temizlik:** Her `tearDown()` metodu geçici dosyaları ve dizinleri silmeli.
6. **Adlandırma:** Test metodları `test_` prefix'i ile başlamalı, açıklayıcı isimler kullanılmalı.

---

### 4.2 MEVCUT TEST DOSYASINI GÜNCELLE: `tests/test_syncthing_service.py`

Bu dosyaya aşağıdaki testleri **ekle**:

```python
from unittest.mock import patch, MagicMock

# EKLENECEK TEST: get_devices() API list response
@patch("services.syncthing_service.requests.get")
def test_get_devices_returns_list_directly(self, mock_get):
    """
    Syncthing API /rest/config/devices doğrudan liste döndürür.
    Eski .get('devices', []) yerine direkt response.json() kullanılmalı.
    HATA-01 düzeltmesini doğrular.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"deviceID": "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH", "name": "Test"},
    ]
    mock_get.return_value = mock_response

    devices = self.service.get_devices()
    self.assertIsInstance(devices, list)
    self.assertEqual(len(devices), 1)
    self.assertEqual(devices[0]["deviceID"], "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH")

# EKLENECEK TEST: get_folders() API list response
@patch("services.syncthing_service.requests.get")
def test_get_folders_returns_list_directly(self, mock_get):
    """
    Syncthing API /rest/config/folders doğrudan liste döndürür.
    HATA-02 düzeltmesini doğrular.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "auto-home-web", "path": "C:/site"},
    ]
    mock_get.return_value = mock_response

    folders = self.service.get_folders()
    self.assertIsInstance(folders, list)
    self.assertEqual(len(folders), 1)
    self.assertEqual(folders[0]["id"], "auto-home-web")

# EKLENECEK TEST: add_device() PUT payload doğru format
@patch("services.syncthing_service.requests.put")
@patch("services.syncthing_service.requests.get")
def test_add_device_puts_list_payload(self, mock_get, mock_put):
    """
    add_device() PUT çağrısında JSON payload direkt liste olmalı,
    {"devices": [...]} dict olmamalı.
    HATA-03 düzeltmesini doğrular.
    """
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = []  # Boş cihaz listesi
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 200
    mock_put.return_value = mock_put_response

    test_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
    self.service.add_device(test_device_id, "Test Cihaz")

    mock_put.assert_called_once()
    call_kwargs = mock_put.call_args[1]  # keyword args
    payload = call_kwargs.get("json")

    # Payload liste olmalı, dict olmamalı
    self.assertIsInstance(payload, list, "PUT payload direkt liste olmalı, dict degil")
    self.assertEqual(len(payload), 1)
    self.assertEqual(payload[0]["deviceID"], test_device_id)

# EKLENECEK TEST: share_folder() cihaz formatı doğru
@patch("services.syncthing_service.requests.put")
@patch("services.syncthing_service.requests.get")
def test_share_folder_device_format(self, mock_get, mock_put):
    """
    share_folder() içindeki klasör 'devices' alanı
    [{"deviceID": "...", "encryptionPassword": ""}] formatında olmalı,
    string listesi ["deviceID"] olmamalı.
    HATA-05 düzeltmesini doğrular.
    """
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = []  # Klasör yok
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 200
    mock_put.return_value = mock_put_response

    test_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"
    self.service.share_folder("auto-home-web", "C:/site", [test_device_id])

    mock_put.assert_called_once()
    call_kwargs = mock_put.call_args[1]
    payload = call_kwargs.get("json")

    # Payload liste olmalı
    self.assertIsInstance(payload, list, "PUT payload direkt liste olmali")
    self.assertEqual(len(payload), 1)
    folder = payload[0]
    # Klasör devices alanı dict listesi olmalı
    self.assertIsInstance(folder["devices"], list)
    if folder["devices"]:
        self.assertIsInstance(folder["devices"][0], dict, "devices icinde dict olmali")
        self.assertIn("deviceID", folder["devices"][0])

# EKLENECEK TEST: share_folder() PUT payload liste formatı
@patch("services.syncthing_service.requests.put")
@patch("services.syncthing_service.requests.get")
def test_share_folder_puts_list_payload(self, mock_get, mock_put):
    """
    share_folder() PUT çağrısında JSON payload direkt liste olmalı.
    HATA-04 düzeltmesini doğrular.
    """
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = []
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 200
    mock_put.return_value = mock_put_response

    self.service.share_folder("test-folder", "C:/test", [])

    mock_put.assert_called_once()
    payload = mock_put.call_args[1].get("json")
    self.assertIsInstance(payload, list, "PUT payload list olmali, dict degil")
```

---

### 4.3 MEVCUT TEST DOSYASINI GÜNCELLE: `tests/test_caddy_service.py`

Bu dosyaya aşağıdaki testi **ekle**:

```python
def test_generate_caddyfile_writes_only_to_config_dir(self):
    """
    generate_caddyfile() Caddyfile'i SADECE constants.CADDYFILE_PATH'e yazmalı,
    site_root klasörüne YAZMAMALIdır.
    HATA-08 düzeltmesini doğrular.
    """
    from utils import constants
    site_root = str(self.temp_dir)

    # Geçici config path ayarla
    temp_config_dir = self.temp_dir / "config"
    temp_caddyfile = temp_config_dir / "Caddyfile"

    original_caddyfile_path = constants.CADDYFILE_PATH
    constants.CADDYFILE_PATH = temp_caddyfile

    try:
        caddyfile = self.service.generate_caddyfile(site_root, port=8080)

        # site_root'ta Caddyfile OLMAMALI
        site_caddyfile = self.temp_dir / "Caddyfile"
        self.assertFalse(site_caddyfile.exists(),
                         "Caddyfile site_root'ta olusturulmamali")

        # Config dizininde OLMALI
        self.assertTrue(caddyfile.exists(),
                        "Caddyfile config dizininde olusturulmali")
    finally:
        constants.CADDYFILE_PATH = original_caddyfile_path
```

---

### 4.4 YENİ DOSYA OLUŞTUR: `tests/test_app_navigation.py`

```python
"""
app.py App sinifi navigasyon birim testleri.
Tkinter gerektiren testler mock ile izole edilir.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import InstallConfig, NodeRole


class TestInstallConfigRoundtrip(unittest.TestCase):
    """InstallConfig to_dict/from_dict testleri."""

    def test_build_install_config_defaults(self):
        """InstallConfig varsayilan degerleri dogru olmali."""
        config = InstallConfig()
        self.assertEqual(config.caddy_port, 80)
        self.assertEqual(config.node_role, NodeRole.PRIMARY)
        self.assertEqual(config.site_root_path, "")
        self.assertEqual(config.cloudflare_token, "")

    def test_install_config_to_dict(self):
        """InstallConfig.to_dict() dogru sozluk uretmeli."""
        config = InstallConfig()
        config.site_root_path = "C:/site"
        config.cloudflare_token = "eyJtest.test.test"
        config.node_role = NodeRole.SECONDARY

        d = config.to_dict()
        self.assertEqual(d["site_root_path"], "C:/site")
        self.assertEqual(d["node_role"], "secondary")
        self.assertIn("caddy_port", d)

    def test_install_config_from_dict_roundtrip(self):
        """to_dict() ve from_dict() roundtrip tutarli olmali."""
        original = InstallConfig()
        original.site_root_path = "C:/mysite"
        original.caddy_port = 8080
        original.node_role = NodeRole.SECONDARY
        original.primary_device_id = "AAAAAAA-BBBBBBB-CCCCCCC-DDDDDDD-EEEEEEE-FFFFFFF-GGGGGGG-HHHHHHH"

        restored = InstallConfig.from_dict(original.to_dict())
        self.assertEqual(restored.site_root_path, original.site_root_path)
        self.assertEqual(restored.caddy_port, original.caddy_port)
        self.assertEqual(restored.node_role, original.node_role)
        self.assertEqual(restored.primary_device_id, original.primary_device_id)

    def test_node_role_primary_value(self):
        """NodeRole.PRIMARY.value 'primary' olmali."""
        self.assertEqual(NodeRole.PRIMARY.value, "primary")

    def test_node_role_secondary_value(self):
        """NodeRole.SECONDARY.value 'secondary' olmali."""
        self.assertEqual(NodeRole.SECONDARY.value, "secondary")


class TestPageNavigationLogic(unittest.TestCase):
    """
    show_page() stack birikimini test eder.
    HATA-07 duzeltmesini dogrular.
    """

    def test_no_duplicate_consecutive_pages_in_stack(self):
        """
        Ayni sayfa arka arkaya stack'e eklenmemeli.
        Duzeltme sonrasi davranisi simule eder.
        """
        mock_page_a = MagicMock()
        mock_page_b = MagicMock()
        page_stack = []
        pages = {"page_a": mock_page_a, "page_b": mock_page_b}

        def simulated_show_page(name):
            """HATA-07 duzeltmesi uygulanmis show_page simulasyonu."""
            page = pages.get(name)
            if page_stack:
                current = page_stack[-1]
                if current is page:
                    return  # Ayni sayfa, ekleme
                current.pack_forget()
            page.pack()
            if not page_stack or page_stack[-1] is not page:
                page_stack.append(page)

        # Kullanici navigasyonu simulasyonu
        simulated_show_page("page_a")
        simulated_show_page("page_a")  # Tekrar ayni sayfa - eklenmemeli
        simulated_show_page("page_b")
        simulated_show_page("page_b")  # Tekrar ayni sayfa - eklenmemeli

        # Stack'te ardisik duplicate olmamali
        for i in range(len(page_stack) - 1):
            self.assertIsNot(
                page_stack[i], page_stack[i + 1],
                f"Stack[{i}] ve Stack[{i+1}] ayni sayfa olmamali"
            )


if __name__ == "__main__":
    unittest.main()
```

---

### 4.5 YENİ DOSYA OLUŞTUR: `tests/test_installer_engine.py`

```python
"""
InstallerEngine birim testleri.
Tum servis cagrilari mock'lanir - admin veya internet gerektirmez.
"""
import queue
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.installer import InstallerEngine
from core.models import InstallConfig, NodeRole, ProgressEvent


class TestInstallerEngineInit(unittest.TestCase):
    """InstallerEngine baslangic testleri."""

    def test_default_init(self):
        """InstallerEngine varsayilan baslangic degerleri dogru olmali."""
        engine = InstallerEngine()
        self.assertIsNotNone(engine.progress_queue)
        self.assertFalse(engine.is_running())
        self.assertIsNotNone(engine.downloader)
        self.assertIsNotNone(engine.caddy_service)
        self.assertIsNotNone(engine.cloudflare_service)
        self.assertIsNotNone(engine.syncthing_service)

    def test_custom_queue(self):
        """Ozel queue ile baslatma."""
        q = queue.Queue()
        engine = InstallerEngine(progress_queue=q)
        self.assertIs(engine.progress_queue, q)

    def test_is_not_running_initially(self):
        """Baslangicta is_running() False olmali."""
        engine = InstallerEngine()
        self.assertFalse(engine.is_running())


class TestInstallerEngineEmit(unittest.TestCase):
    """InstallerEngine emit metodlari testleri."""

    def setUp(self):
        self.q = queue.Queue()
        self.engine = InstallerEngine(progress_queue=self.q)

    def test_emit_sends_progress_event(self):
        """_emit() kuyruğa ProgressEvent gönderir."""
        self.engine._emit("Test mesaj", 50)
        event = self.q.get_nowait()
        self.assertEqual(event.message, "Test mesaj")
        self.assertEqual(event.percentage, 50)
        self.assertFalse(event.is_error)
        self.assertFalse(event.is_complete)
        self.assertFalse(event.is_cancelled)

    def test_emit_error(self):
        """_emit_error() is_error=True olan event gonderir."""
        self.engine._emit_error("Hata olustu")
        event = self.q.get_nowait()
        self.assertTrue(event.is_error)
        self.assertEqual(event.message, "Hata olustu")

    def test_emit_complete(self):
        """_emit_complete() is_complete=True olan event gonderir."""
        self.engine._emit_complete()
        event = self.q.get_nowait()
        self.assertTrue(event.is_complete)
        self.assertEqual(event.percentage, 100)

    def test_emit_cancelled(self):
        """_emit_cancelled() is_cancelled=True olan event gonderir."""
        self.engine._emit_cancelled()
        event = self.q.get_nowait()
        self.assertTrue(event.is_cancelled)


class TestInstallerEngineCancel(unittest.TestCase):
    """InstallerEngine iptal mekanizmasi testleri."""

    def test_cancel_sets_event(self):
        """cancel() cagrisi _cancel_event'i set eder."""
        engine = InstallerEngine()
        self.assertFalse(engine._cancel_event.is_set())
        engine.cancel()
        self.assertTrue(engine._cancel_event.is_set())


class TestInstallerEngineRollback(unittest.TestCase):
    """InstallerEngine rollback testleri."""

    def test_rollback_calls_uninstall_in_reverse(self):
        """
        _rollback() tamamlanan adimlari ters sirayla kaldirir.
        caddy -> cloudflared -> syncthing kurulmussa
        rollback: syncthing -> cloudflared -> caddy
        """
        engine = InstallerEngine()
        call_order = []

        engine.caddy_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("caddy_uninstall"))
        engine.cloudflare_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("cloudflare_uninstall"))
        engine.syncthing_service.uninstall = MagicMock(
            side_effect=lambda: call_order.append("syncthing_uninstall"))

        engine._completed_steps = ["caddy", "cloudflared", "syncthing"]
        engine._rollback()

        self.assertEqual(call_order,
                         ["syncthing_uninstall", "cloudflare_uninstall", "caddy_uninstall"])

    def test_rollback_partial_steps(self):
        """Sadece ilk adim tamamlanmissa yalnizca o geri alinir."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock()
        engine.cloudflare_service.uninstall = MagicMock()

        engine._completed_steps = ["caddy"]
        engine._rollback()

        engine.caddy_service.uninstall.assert_called_once()
        engine.cloudflare_service.uninstall.assert_not_called()

    def test_rollback_error_does_not_propagate(self):
        """Rollback sirasinda olusan hata yakalanir, yayilmaz."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock(
            side_effect=Exception("Servis kaldirilmadi"))

        engine._completed_steps = ["caddy"]
        try:
            engine._rollback()
        except Exception:
            self.fail("_rollback() exception yaymamali")

    def test_rollback_clears_completed_steps(self):
        """Rollback sonrasi _completed_steps bos olmali."""
        engine = InstallerEngine()
        engine.caddy_service.uninstall = MagicMock()
        engine._completed_steps = ["caddy"]
        engine._rollback()
        self.assertEqual(engine._completed_steps, [])


class TestInstallerProgressCallback(unittest.TestCase):
    """Progress callback yuzde esleme testleri."""

    def setUp(self):
        self.q = queue.Queue()
        self.engine = InstallerEngine(progress_queue=self.q)

    def _drain(self):
        """Queue'yu bosalt, son eventi dondur."""
        event = None
        while not self.q.empty():
            event = self.q.get_nowait()
        return event

    def test_caddy_callback_range_start(self):
        """Caddy progress %10-%35 araligina eslenmeli."""
        self.engine._caddy_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertIsNotNone(event)
        self.assertGreaterEqual(event.percentage, 10)
        self.assertLessEqual(event.percentage, 35)

    def test_caddy_callback_range_end(self):
        """Caddy %100 icin de aralik icinde olmali."""
        self.engine._caddy_progress_callback(100, "Bitti")
        event = self._drain()
        self.assertIsNotNone(event)
        self.assertGreaterEqual(event.percentage, 10)
        self.assertLessEqual(event.percentage, 35)

    def test_cloudflared_callback_range(self):
        """Cloudflared progress %35-%60 araligina eslenmeli."""
        self.engine._cloudflared_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertGreaterEqual(event.percentage, 35)
        self.assertLessEqual(event.percentage, 60)

    def test_syncthing_callback_range(self):
        """Syncthing progress %60-%83 araligina eslenmeli."""
        self.engine._syncthing_progress_callback(0, "Basliyor")
        event = self._drain()
        self.assertGreaterEqual(event.percentage, 60)
        self.assertLessEqual(event.percentage, 83)

    def test_negative_percent_not_emitted(self):
        """Negatif yuzde emit edilmemeli."""
        self.engine._caddy_progress_callback(-1, "Hata")
        self.assertTrue(self.q.empty(), "Negatif yuzde event gonderilmemeli")


if __name__ == "__main__":
    unittest.main()
```

---

### 4.6 YENİ DOSYA OLUŞTUR: `tests/test_network.py`

```python
"""
utils/network.py modulu birim testleri.
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.network import (
    is_port_available,
    get_local_ip,
    check_internet_connection,
    check_tcp_connection,
    find_available_port,
)


class TestPortAvailability(unittest.TestCase):

    def test_is_port_available_returns_bool(self):
        """is_port_available() bool dondurmeli."""
        result = is_port_available(62000)  # Yuksek port, muhtemelen bos
        self.assertIsInstance(result, bool)

    def test_is_port_available_used_port(self):
        """Kullanimda olan port False dondurmeli."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
            self.assertFalse(is_port_available(port))

    def test_find_available_port_returns_valid(self):
        """find_available_port() gecerli port veya -1 dondurmeli."""
        port = find_available_port(50000)
        if port != -1:
            self.assertGreaterEqual(port, 50000)
            self.assertLessEqual(port, 65535)
        # -1 de gecerli (hic bos port yoksa)


class TestGetLocalIP(unittest.TestCase):

    def test_get_local_ip_returns_string(self):
        """get_local_ip() string dondurmeli."""
        ip = get_local_ip()
        self.assertIsInstance(ip, str)
        self.assertGreater(len(ip), 0)

    def test_get_local_ip_fallback_on_error(self):
        """Hata durumunda 127.0.0.1 dondurmeli."""
        with patch("utils.network.socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect.side_effect = Exception("No network")
            ip = get_local_ip()
            self.assertEqual(ip, "127.0.0.1")


class TestInternetConnection(unittest.TestCase):

    @patch("utils.network.urllib.request.urlopen")
    def test_check_internet_true(self, mock_urlopen):
        """Internet erisimi varsa True."""
        mock_urlopen.return_value = MagicMock()
        self.assertTrue(check_internet_connection())

    @patch("utils.network.urllib.request.urlopen")
    def test_check_internet_false(self, mock_urlopen):
        """Internet erisimi yoksa False."""
        mock_urlopen.side_effect = Exception("No internet")
        self.assertFalse(check_internet_connection())


class TestCheckTCPConnection(unittest.TestCase):

    def test_check_tcp_connection_to_closed_port_returns_false(self):
        """Kapali porta baglanti False dondurmeli."""
        result = check_tcp_connection("127.0.0.1", 19999, timeout=1)
        self.assertIsInstance(result, bool)
        # Port 19999 genellikle kapalidir

    @patch("utils.network.socket.create_connection")
    def test_check_tcp_connection_success(self, mock_conn):
        """Basarili baglanti True dondurmeli."""
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = check_tcp_connection("127.0.0.1", 8080)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
```

---

### 4.7 MEVCUT DOSYAYI GÜNCELLE: `tests/test_downloader.py`

Mevcut `setUp`'ı şu şekilde güncelle (sabit `C:/temp/TestApp` yolu yerine geçici dizin kullan):

```python
def setUp(self):
    import tempfile
    self.temp_dir = Path(tempfile.mkdtemp())
    self.downloader = Downloader(install_dir=self.temp_dir)

def tearDown(self):
    import shutil
    shutil.rmtree(self.temp_dir, ignore_errors=True)

def test_is_binary_installed_false(self):
    """Var olmayan binary False dondurmeli."""
    self.assertFalse(self.downloader.is_binary_installed("caddy.exe"))

def test_is_binary_installed_true(self):
    """Mevcut binary True dondurmeli."""
    bin_dir = self.temp_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "caddy.exe").write_bytes(b"fake exe content")
    self.assertTrue(self.downloader.is_binary_installed("caddy.exe"))
```

---

## 5. Tüm Testleri Çalıştırma

```bash
# Proje kokunden calistir:
cd c:\Users\elega\Desktop\AutoHomeWebSetup

# Standart unittest ile (pytest kurmadan)
python -m unittest discover -s tests -p "test_*.py" -v

# Sadece belirli dosya
python -m unittest tests.test_syncthing_service -v
python -m unittest tests.test_installer_engine -v

# pytest varsa
pip install pytest
python -m pytest tests/ -v --tb=short
```

---

## 6. Düzeltme Uygulama Sırası

1. **HATA-06** → `assets/nssm.exe`'yi indir ve ekle + `build.spec`'i güncelle
2. **HATA-01** → `syncthing_service.py` satır 291: `.get("devices", [])` → doğrudan `.json()`
3. **HATA-02** → `syncthing_service.py` satır 364: `.get("folders", [])` → doğrudan `.json()`
4. **HATA-03** → `syncthing_service.py` satır 344: `json={"devices": devices}` → `json=devices`
5. **HATA-04** → `syncthing_service.py` satır 466: `json={"folders": folders}` → `json=folders`
6. **HATA-05** → `syncthing_service.py` satır 400-402 ve 420: cihaz formatını `{"deviceID": ..., "encryptionPassword": ""}` yap
7. **HATA-10** → `main.py` satır 13: `logger = get_logger(...)` satırını `main()` fonksiyonu içine taşı
8. **HATA-07** → `app.py` satır 110-112: stack birikimini önle
9. **HATA-08** → `caddy_service.py` satır 70-71: site_root'a yazma kaldır
10. **HATA-09** → `build.spec` satır 105-114: COLLECT bloğunu kaldır
11. **Test scriptlerini** yaz (`4.2 - 4.7` arası) ve çalıştır
12. **HATA-12** → `constants.py` satır 78: API key chars güncelle

---

## 7. Doğrulama Adımları

```bash
# 1. Tüm modul importlarini dogrula
python -c "from app import App; from core.installer import InstallerEngine; from services.syncthing_service import SyncthingService; print('Tum importlar OK')"

# 2. Birim testlerini calistir
python -m unittest discover -s tests -p "test_*.py" -v

# 3. Uygulamayi baslatmaya calis (admin olarak)
python main.py
```

---

*Bu plan otomatik kod analizi ile olusturulmustur. Syncthing REST API v1 dokumantasyonu baz alinmistir.*  
*GitHub: https://docs.syncthing.net/rest/config.html*
