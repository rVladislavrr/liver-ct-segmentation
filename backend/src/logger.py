import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_LOG_FILE = LOG_DIR / "database.log"
API_LOG_FILE = LOG_DIR / "api.log"
S3_LOG_FILE = LOG_DIR / "s3_logger.log"

LOG_FORMAT = '%(levelname)s: %(name)s - %(message)s - %(asctime)s'

class ExtraFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, '__dict__'):
            extra_data = {k: v for k, v in record.__dict__.items()
                         if k not in logging.LogRecord('', '', '', '', '', '', '').__dict__}
            if extra_data:
                record.msg = f"{record.msg} - {extra_data}"
        return super().format(record)

def setup_logger(name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = ExtraFormatter('%(levelname)s: %(name)s - %(message)s - %(asctime)s')

    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


database_logger = setup_logger('database', DATABASE_LOG_FILE)
api_logger = setup_logger('api', API_LOG_FILE)
s3_logger = setup_logger('s3', S3_LOG_FILE)
