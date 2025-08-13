import logging

from google.cloud.logging import Client as CloudLoggingClient
from google.cloud.logging.handlers import CloudLoggingHandler

from src.core.config import settings


def setup_logger(name: str, level: int = logging.INFO, cloud_logging: bool = False) -> logging.Logger:
    """Setup logger

    Args:
        name (str): logger name
        level (int): logger level
        cloud_logging (bool): whether to use cloud logging

    Returns:
        logging.Logger: logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        if cloud_logging:
            try:
                cloud_logging_client = CloudLoggingClient(project=settings.PROJECT_ID)
                handler = CloudLoggingHandler(cloud_logging_client, name=name)
                # Cloud Logging doesn't need custom formatter
            except Exception as e:
                print(f"Cloud Logging initialization failed, falling back to StreamHandler: {e}")
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                handler.setFormatter(formatter)
        else:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


logger = setup_logger(name=settings.APP_NAME, cloud_logging=settings.CLOUD_LOGGING)
