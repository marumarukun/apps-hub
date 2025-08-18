from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application"""

    APP_NAME: str = "gradio-chatbot"
    PROJECT_ID: str = ""
    CLOUD_LOGGING: bool = False
    OPENAI_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    """Get the settings

    Returns:
        Settings: The settings
    """
    return Settings()


settings = get_settings()