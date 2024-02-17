from .config import AppConfig
from .logging.config import LoggingConfig


def init_app() -> dict:
    LoggingConfig().load()
    return AppConfig().load()
