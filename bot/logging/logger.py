import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger(name: str = "winner_bot") -> logging.Logger:
    os.makedirs("bot/data/logs", exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("bot/data/logs/app.log", maxBytes=2_000_000, backupCount=5)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger

