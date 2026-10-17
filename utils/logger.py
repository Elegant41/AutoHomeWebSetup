"""
Dosya + GUI tabanlı loglama.

Hem dosyaya (C:\\ProgramData\\AutoHomeWebSetup\\logs\\installer.log)
hem de isteğe bağlı olarak GUI'ye (queue üzerinden) log gönderir.
"""

import logging
import queue
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils import constants


class GUIQueueHandler(logging.Handler):
    """
    Log kayıtlarını thread-safe bir queue'ya gönderen logging handler.

    GUI tarafı bu queue'yu periyodik olarak poll eder ve log mesajlarını
    ekrana yansıtır.
    """

    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            # Loglama hataları asla ana akışı bozmamalı
            pass


# ─── Singleton Logger Yönetimi ────────────────────────────────────────
_logger: logging.Logger | None = None
_logger_lock = threading.Lock()
_gui_queue: queue.Queue | None = None


def _get_logger() -> logging.Logger:
    """Logger'ı oluşturur (thread-safe singleton)."""
    global _logger
    with _logger_lock:
        if _logger is not None:
            return _logger

        app_logger = logging.getLogger(constants.APP_NAME)
        app_logger.setLevel(logging.DEBUG)
        app_logger.propagate = False

        # Dosya handler'ı
        log_file = Path(constants.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(constants.LOG_FORMAT, constants.LOG_DATE_FORMAT)
        )
        app_logger.addHandler(file_handler)

        # Konsol handler'ı (geliştirme sırasında)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter(constants.LOG_FORMAT, constants.LOG_DATE_FORMAT)
        )
        app_logger.addHandler(console_handler)

        _logger = app_logger
        return app_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Logger nesnesini döndürür.

    Args:
        name: Logger adı (opsiyonel, varsayılan: AutoHomeWebSetup)

    Returns:
        logging.Logger nesnesi
    """
    base = _get_logger()
    if name is None:
        return base
    return logging.getLogger(f"{constants.APP_NAME}.{name}")


def setup_gui_logging(log_queue: queue.Queue) -> None:
    """
    GUI loglama için queue handler'ı ekler.

    Args:
        log_queue: GUI tarafından poll edilecek thread-safe queue
    """
    global _gui_queue
    _gui_queue = log_queue

    handler = GUIQueueHandler(log_queue)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", constants.LOG_DATE_FORMAT)
    )
    _get_logger().addHandler(handler)


def log_debug(msg: str) -> None:
    get_logger().debug(msg)


def log_info(msg: str) -> None:
    get_logger().info(msg)


def log_warning(msg: str) -> None:
    get_logger().warning(msg)


def log_error(msg: str) -> None:
    get_logger().error(msg)

def log_exception(msg: str = "") -> None:
    get_logger().exception(msg)