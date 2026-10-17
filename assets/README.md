# Assets Klasörü

Bu dizin, PyInstaller ile derleme sırasında exe'ye gömülecek statik kaynakları içerir.

## Gerekli Dosyalar

- `icon.ico` — Uygulama ikonu (256x256, Windows ICO formatı)
- `logo.png` — Hoşgeldiniz sayfası logosu
- `banner.png` — Sihirbaz banner'ı
- `nssm.exe` — NSSM binary'si (~300KB)

Bu dosyaların exe'ye gömülebilmesi için `build.spec` dosyasındaki `datas` listesine eklenmesi gerekir.

> **Not:** `nssm.exe` eksikse, `Downloader.setup_nssm()` metodu otomatik olarak İnternet'ten indirir.