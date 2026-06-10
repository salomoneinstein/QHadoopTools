import logging
from typing import Optional
from .config import Config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Factory for configured loggers.
    Ensures no duplicate handlers.
    """

    logger = logging.getLogger(name if name else "QHadoopTools")

    if logger.handlers:
        return logger

    level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(Config.LOG_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

logger = get_logger()