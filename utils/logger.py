import logging
from typing import Optional

from .config import Config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Factory for creating configured loggers.
    Prevents duplicate handlers.
    """

    logger = logging.getLogger(name if name else "QHadoopTools")

    if not logger.handlers:
        level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)

        logger.setLevel(level)

        # Console handler
        handler = logging.StreamHandler()

        formatter = logging.Formatter(Config.LOG_FORMAT)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


# Default logger instance
logger = get_logger()
