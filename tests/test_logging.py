import logging
import os
from pathlib import Path
from diskest.utils.logging import setup_logging, get_log_file_path


def test_setup_logging(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging(verbose=True, log_file=str(log_file))

    logger = logging.getLogger("diskest")
    root_logger = logging.getLogger()

    assert logger.level == logging.DEBUG
    assert any(isinstance(h, logging.FileHandler) for h in root_logger.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)

    file_handlers = [
        h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert file_handlers, "No FileHandler found in root logger"

    assert (
        os.path.exists(log_file) or file_handlers[0].baseFilename != "/dev/null"
    ), f"Log file {log_file} was not created and handler is not properly configured"


def test_get_log_file_path():
    log_path = get_log_file_path()
    assert isinstance(log_path, Path)
    assert log_path.name == "diskest.log"
    assert str(log_path).startswith("/var/log/diskest")
