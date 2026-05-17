import logging

from app.core.logging import get_logger


def test_get_logger_returns_logger() -> None:
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "mingmax"


def test_get_logger_returns_same_instance() -> None:
    logger1 = get_logger()
    logger2 = get_logger()

    assert logger1 is logger2
