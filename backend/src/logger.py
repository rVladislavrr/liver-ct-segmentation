import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_LOG_FILE = LOG_DIR / "database.log"
API_LOG_FILE = LOG_DIR / "api.log"

LOG_FORMAT = '%(levelname)s: %(name)s - %(message)s - %(asctime)s'


def setup_logger(name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


database_logger = setup_logger('database', DATABASE_LOG_FILE)
api_logger = setup_logger('api', API_LOG_FILE)
