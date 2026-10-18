import logging
import queue
import threading
from unittest.mock import patch, MagicMock

import pytest

from utils import logger, constants


@pytest.fixture(autouse=True)
def reset_logger():
    """Fixture to reset the logger singleton before each test."""
    logger._logger = None
    logger._gui_queue = None
    with logger._logger_lock:
        pass # just to ensure it's not locked if it was
    yield
    logger._logger = None
    logger._gui_queue = None


def test_get_logger_singleton():
    """Test that get_logger returns a singleton instance."""
    logger1 = logger.get_logger()
    logger2 = logger.get_logger()

    assert isinstance(logger1, logging.Logger)
    assert logger1 is logger2
    assert logger1.name == constants.APP_NAME


def test_get_logger_named():
    """Test that get_logger with a name returns a properly named logger."""
    named_logger = logger.get_logger("test_module")

    assert isinstance(named_logger, logging.Logger)
    assert named_logger.name == f"{constants.APP_NAME}.test_module"

    # Should use the same root setup, but different logger instances due to the way getLogger works
    named_logger2 = logger.get_logger("test_module")
    assert named_logger is named_logger2


def test_setup_gui_logging():
    """Test setting up GUI logging adds the correct handler."""
    q = queue.Queue()
    logger.setup_gui_logging(q)

    app_logger = logger.get_logger()
    gui_handlers = [h for h in app_logger.handlers if isinstance(h, logger.GUIQueueHandler)]

    assert len(gui_handlers) == 1
    assert gui_handlers[0].log_queue is q
    assert logger._gui_queue is q


def test_gui_queue_handler_emit():
    """Test that GUIQueueHandler puts formatted messages in the queue."""
    q = queue.Queue()
    handler = logger.GUIQueueHandler(q)
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )

    handler.emit(record)

    assert not q.empty()
    msg = q.get()
    assert msg == "INFO - Test message"


def test_gui_queue_handler_emit_exception():
    """Test that GUIQueueHandler handles queue put exceptions gracefully."""
    q = MagicMock(spec=queue.Queue)
    q.put.side_effect = Exception("Queue error")

    handler = logger.GUIQueueHandler(q)

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )

    # Should not raise
    handler.emit(record)
    q.put.assert_called_once()


@patch("utils.logger.get_logger")
def test_log_functions(mock_get_logger):
    """Test the convenient log functions call the underlying logger methods."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    logger.log_debug("debug msg")
    mock_logger.debug.assert_called_once_with("debug msg")

    logger.log_info("info msg")
    mock_logger.info.assert_called_once_with("info msg")

    logger.log_warning("warning msg")
    mock_logger.warning.assert_called_once_with("warning msg")

    logger.log_error("error msg")
    mock_logger.error.assert_called_once_with("error msg")

    logger.log_exception("exception msg")
    mock_logger.exception.assert_called_once_with("exception msg")
