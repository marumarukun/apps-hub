import logging

from src.core.config import settings


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logger

    Args:
        name (str): logger name
        level (int): logger level

    Returns:
        logging.Logger: logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger(name=settings.APP_NAME)
