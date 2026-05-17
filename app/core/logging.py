import logging

from app.core.config import get_settings

_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        settings = get_settings()
        _logger = logging.getLogger(settings.app_name)
        if not _logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
        _logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    return _logger
