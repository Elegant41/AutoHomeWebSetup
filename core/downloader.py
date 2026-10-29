"""
İndirme Motoru.

GitHub Releases API'den Caddy, Cloudflared ve Syncthing binary'lerini
indirir. SHA256 hash doğrulaması yapar. Chunk-based indirme + ilerleme
yüzdesi ve exponential backoff retry destekler.
"""

import hashlib
import io
import threading
import time
import zipfile
from pathlib import Path
from typing import Callable, Optional

import requests

from utils import constants
from utils.logger import get_logger
from utils.platform_utils import is_valid_binary, run_command
from utils.resource_path import resource_path

logger = get_logger(__name__)

ProgressCallback = Optional[Callable[[int, str], None]]


class DownloadError(Exception):
    """İndirme sırasında oluşan hatalar için özel istisna."""

    pass


class DownloadCancelledError(DownloadError):
    """İndirme kullanıcı tarafından iptal edildiğinde oluşan istisna."""

    pass


class HashMismatchError(DownloadError):
    """SHA256 hash doğrulaması başarısız olduğunda oluşan hata."""

    pass


class Downloader:
    """
    Bileşen indirme ve kurulum yönetimi.
    """

    def __init__(
        self,
        install_dir: Path | None = None,
        cancel_event: Optional[threading.Event] = None,
    ):
        self.install_dir = install_dir or constants.INSTALL_DIR
        self.bin_dir = self.install_dir / "bin"
        self.cancel_event = cancel_event
        self._expected_hashes: dict[str, str] = {}

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": f"{constants.APP_NAME}/{constants.APP_VERSION}",
            "Accept": "application/octet-stream",
        })

    def _check_cancelled(self, dest: Optional[Path] = None) -> None:
        """İptal sinyali gelmişse kısmi dosyayı siler ve istisna fırlatır."""
        if self.cancel_event and self.cancel_event.is_set():
            if dest and dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            raise DownloadCancelledError("İndirme kullanıcı tarafından iptal edildi.")

    # ─── Genel İndirme ──────────────────────────────────────────────
    def download_file(
        self,
        url: str,
        dest: Path,
        progress_callback: ProgressCallback = None,
        timeout: int = constants.DOWNLOAD_TIMEOUT,
    ) -> Path:
        """
        Dosyayı chunk-based olarak indirir.

        Args:
            url: İndirilecek dosyanın URL'si
            dest: Hedef dosya yolu
            progress_callback: (yüzde, mesaj) çağrılan geri çağrı
            timeout: Zaman aşımı saniye

        Returns:
            Path: İndirilen dosyanın yolu

        Raises:
            DownloadError: İndirme başarısız olursa
        """
        # Üst dizini oluştur
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Exponential backoff retry
        retry_count = constants.DOWNLOAD_RETRY_COUNT
        retry_delay = constants.DOWNLOAD_RETRY_DELAY

        for attempt in range(1, retry_count + 1):
            self._check_cancelled(dest)
            try:
                logger.info(f"İndiriliyor: {url} (deneme {attempt}/{retry_count})")
                if progress_callback:
                    progress_callback(0, f"İndiriliyor: {dest.name}")

                with self._session.get(url, stream=True, timeout=timeout) as response:
                    response.raise_for_status()

                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with open(dest, "wb") as f:
                        for chunk in response.iter_content(chunk_size=constants.DOWNLOAD_CHUNK_SIZE):
                            self._check_cancelled(dest)
                            if not chunk:
                                continue
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0 and progress_callback:
                                percent = int((downloaded / total_size) * 100)
                                progress_callback(percent, f"İndiriliyor: {dest.name} (%{percent})")

                if progress_callback:
                    progress_callback(100, f"İndirme tamamlandı: {dest.name}")

                # Dosya boyutu kontrolü
                if total_size > 0 and dest.stat().st_size != total_size:
                    raise DownloadError(
                        f"Dosya boyutu eşleşmiyor: {dest.stat().st_size} != {total_size}"
                    )

                # Eğer GitHub API'den SHA256 digest bilgisi alındıysa doğrula
                expected_sha256 = self._expected_hashes.get(url, "")
                if expected_sha256:
                    self.verify_sha256(dest, expected_sha256)

                logger.info(f"İndirme başarılı: {dest} ({dest.stat().st_size} bayt)")
                return dest

            except DownloadCancelledError:
                raise
            except HashMismatchError:
                if dest.exists():
                    try:
                        dest.unlink()
                    except OSError:
                        pass
                raise
            except requests.RequestException as e:
                if dest.exists():
                    try:
                        dest.unlink()
                    except OSError:
                        pass
                if attempt < retry_count:
                    wait = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"İndirme hatası (deneme {attempt}): {e}. {wait}s sonra tekrar...")
                    if progress_callback:
                        progress_callback(-1, f"Bağlantı hatası, {wait}s sonra tekrar deneniyor...")
                    for _ in range(int(wait * 10)):
                        self._check_cancelled(dest)
                        time.sleep(0.1)
                else:
                    raise DownloadError(f"İndirme başarısız: {url} → {e}") from e

            except OSError as e:
                if dest.exists():
                    try:
                        dest.unlink()
                    except OSError:
                        pass
                raise DownloadError(f"Dosya yazma hatası: {e}") from e

        raise DownloadError(f"İndirme başarısız: {url}")

    # ─── SHA256 Doğrulama ───────────────────────────────────────────
    def verify_sha256(self, file_path: Path, expected_hash: str) -> bool:
        """
        Dosyanın SHA256 hash'ini doğrular.

        Args:
            file_path: Doğrulanacak dosya
            expected_hash: Beklenen SHA256 hash değeri

        Returns:
            bool: Hash eşleşiyorsa True

        Raises:
            HashMismatchError: Hash eşleşmezse
        """
        logger.info(f"SHA256 doğrulanıyor: {file_path.name}")

        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        actual_hash = sha256.hexdigest().lower()
        expected_hash = expected_hash.lower().removeprefix("sha256:")

        if actual_hash != expected_hash:
            raise HashMismatchError(
                f"SHA256 eşleşmiyor!\n"
                f"Beklenen: {expected_hash}\n"
                f"Gerçekleşen: {actual_hash}"
            )

        logger.info(f"SHA256 doğrulandı: {file_path.name}")
        return True

    def get_latest_release_url(
        self, repo_api: str, expected_ext: str = ""
    ) -> tuple[str, str]:
        """
        GitHub Releases API'den en son sürümün indirme URL'sini alır.
        Varsa asset'in SHA256 digest bilgisini de kaydeder.

        Args:
            repo_api: GitHub Releases API URL'si
            expected_ext: Beklenen dosya uzantısı

        Returns:
            tuple[str, str]: (indirme_url, sürüm)
        """
        try:
            logger.info(f"En son sürüm alınıyor: {repo_api}")
            response = self._session.get(
                repo_api,
                timeout=30,
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            response.raise_for_status()

            data = response.json()
            version = data.get("tag_name", "").lstrip("v")

            # Windows amd64 asset'ini bul
            assets = data.get("assets", [])
            for asset in assets:
                asset_name = asset.get("name", "")
                if "windows" in asset_name.lower() and "amd64" in asset_name.lower():
                    if expected_ext and not asset_name.lower().endswith(expected_ext.lower()):
                        continue
                    download_url = asset.get("browser_download_url", "")
                    if download_url:
                        digest = asset.get("digest", "")
                        if isinstance(digest, str) and digest.lower().startswith("sha256:"):
                            self._expected_hashes[download_url] = digest.split(":", 1)[1].strip()
                        return download_url, version

            raise DownloadError(f"API yanıtında uygun ({expected_ext}) Windows amd64 asset'i bulunamadı.")

        except requests.RequestException as e:
            raise DownloadError(f"GitHub API çağrısı başarısız: {e}") from e
        except KeyError as e:
            raise DownloadError(f"GitHub API yanıtı beklenen formatta değil: {e}") from e

    # ─── Bileşen İndirmeleri ─────────────────────────────────────────
    def download_caddy(
        self, progress_callback: ProgressCallback = None
    ) -> Path:
        """
        Caddy binary'sini indirir ve zip'ten çıkarır.

        Returns:
            Path: caddy.exe yolu
        """
        try:
            if progress_callback:
                progress_callback(5, "Caddy en son sürümü alınıyor...")

            download_url, version = self.get_latest_release_url(
                constants.CADDY_RELEASE_API,
                expected_ext=".zip",
            )

            zip_path = self.bin_dir / f"caddy_v{version}_windows_amd64.zip"
            self.download_file(download_url, zip_path, progress_callback)

            # Zip'ten caddy.exe'yi çıkar
            caddy_exe = self.bin_dir / constants.CADDY_EXE
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    if member.lower().endswith("caddy.exe") or member.lower() == "caddy.exe":
                        with zf.open(member) as src, open(caddy_exe, "wb") as dst:
                            dst.write(src.read())
                        break
                else:
                    raise DownloadError("Zip içinde caddy.exe bulunamadı")

            # Zip'i temizle
            zip_path.unlink(missing_ok=True)

            logger.info(f"Caddy indirildi: {caddy_exe}")
            return caddy_exe

        except Exception as e:
            if not isinstance(e, DownloadError):
                raise DownloadError(f"Caddy indirme hatası: {e}") from e
            raise

    def download_cloudflared(
        self, progress_callback: ProgressCallback = None
    ) -> Path:
        """
        Cloudflared binary'sini indirir.

        Returns:
            Path: cloudflared.exe yolu
        """
        try:
            if progress_callback:
                progress_callback(5, "Cloudflared en son sürümü alınıyor...")

            download_url, version = self.get_latest_release_url(
                constants.CLOUDFLARED_RELEASE_API,
                expected_ext=".exe",
            )

            cloudflared_exe = self.bin_dir / constants.CLOUDFLARED_EXE
            self.download_file(download_url, cloudflared_exe, progress_callback)

            logger.info(f"Cloudflared indirildi: {cloudflared_exe}")
            return cloudflared_exe

        except Exception as e:
            if not isinstance(e, DownloadError):
                raise DownloadError(f"Cloudflared indirme hatası: {e}") from e
            raise

    def download_syncthing(
        self, progress_callback: ProgressCallback = None
    ) -> Path:
        """
        Syncthing binary'sini indirir ve zip'ten çıkarır.

        Returns:
            Path: syncthing.exe yolu
        """
        try:
            if progress_callback:
                progress_callback(5, "Syncthing en son sürümü alınıyor...")

            download_url, version = self.get_latest_release_url(
                constants.SYNCTHING_RELEASE_API,
                expected_ext=".zip",
            )

            zip_path = self.bin_dir / f"syncthing-windows-amd64-v{version}.zip"
            self.download_file(download_url, zip_path, progress_callback)

            # Zip'ten syncthing.exe'yi çıkar
            syncthing_exe = self.bin_dir / constants.SYNCTHING_EXE
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    if member.lower().endswith("syncthing.exe"):
                        with zf.open(member) as src, open(syncthing_exe, "wb") as dst:
                            dst.write(src.read())
                        break
                else:
                    raise DownloadError("Zip içinde syncthing.exe bulunamadı")

            # Zip'i temizle
            zip_path.unlink(missing_ok=True)

            logger.info(f"Syncthing indirildi: {syncthing_exe}")
            return syncthing_exe

        except Exception as e:
            if not isinstance(e, DownloadError):
                raise DownloadError(f"Syncthing indirme hatası: {e}") from e
            raise

    def setup_nssm(self) -> Path:
        """
        Gömülü nssm.exe'yi _MEIPASS'tan kalıcı dizine kopyalar.

        Returns:
            Path: nssm.exe yolu
        """
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        # Gömülü kaynak
        source = resource_path("assets/nssm.exe")
        dest = self.bin_dir / constants.NSSM_EXE

        if is_valid_binary(dest):
            logger.info(f"NSSM zaten mevcut: {dest}")
            return dest

        if not is_valid_binary(source):
            # NSSM dosyası bulunamazsa veya 0 bayt ise indir
            logger.warning("Gömülü nssm.exe bulunamadı veya geçersiz, indiriliyor...")
            return self._download_nssm()

        # Kopyala
        import shutil

        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass

        shutil.copy2(source, dest)
        logger.info(f"NSSM kopyalandı: {source} → {dest}")
        return dest

    def _download_nssm(self) -> Path:
        """
        NSSM'yi İnternet'ten indirir (gömülü dosya yoksa).

        Returns:
            Path: nssm.exe yolu
        """
        nssm_url = (
            "https://nssm.cc/release/nssm-2.24.zip"
        )
        zip_path = self.bin_dir / "nssm.zip"
        dest = self.bin_dir / constants.NSSM_EXE

        self.download_file(nssm_url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                if member.lower().endswith("nssm.exe") and "win64" in member.lower():
                    with zf.open(member) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                    break
            else:
                raise DownloadError("NSSM zip içinde nssm.exe bulunamadı")

        zip_path.unlink(missing_ok=True)
        logger.info(f"NSSM indirildi: {dest}")
        return dest

    # ─── Yardımcı Metotlar ──────────────────────────────────────────
    def cleanup_temp_files(self) -> None:
        """Geçici indirme dosyalarını temizler."""
        for ext in (".zip", ".tmp", ".part"):
            for f in self.bin_dir.glob(f"*{ext}"):
                try:
                    f.unlink()
                except OSError:
                    pass

    def is_binary_installed(self, name: str) -> bool:
        """Binary dosyasının kurulu ve geçerli olup olmadığını kontrol eder."""
        return is_valid_binary(self.bin_dir / name)