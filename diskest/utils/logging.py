"""
Logging configuration module for Diskest
"""

import logging
from rich.logging import RichHandler
from pathlib import Path


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Set up logging for the Diskest application.

    Args:
        verbose (bool): If True, set logging level to DEBUG.
        Otherwise, set to INFO.
        log_file (str): Path to the log file.
        If None, logging to file is disabled.
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )

    # Configure file logging if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)

    # Silence some overly verbose libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    # Ensure that package's loggers are set to the correct level
    logging.getLogger("diskest").setLevel(level)

    # Log the start of the application
    logging.info("Diskest logging initialized")
    if verbose:
        logging.debug("Verbose logging enabled")
    if log_file:
        logging.info(f"Logging to file: {log_file}")


def get_log_file_path() -> Path:
    """
    Get the default log file path.

    Returns:
        Path: Path to the default log file
    """
    log_dir = Path("/var/log/diskest")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "diskest.log"
