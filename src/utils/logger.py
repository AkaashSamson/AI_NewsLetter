"""
Centralized logging configuration for AI Newsletter
Provides industry-grade logging with file rotation and proper formatting
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = None,
    console: bool = True,
) -> logging.Logger:
    """
    Setup centralized logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        log_file: Custom log file name (default: pipeline_YYYYMMDD.log)
        console: Whether to output logs to console

    Returns:
        Configured root logger
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Default log file with date
    if log_file is None:
        log_file = f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"

    log_filepath = log_path / log_file

    # Create formatter
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # File handler with rotation (10MB max, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_filepath, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # Log startup message
    root_logger.info("=" * 80)
    root_logger.info(f"Logging initialized | Level: {log_level} | File: {log_filepath}")
    root_logger.info("=" * 80)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
