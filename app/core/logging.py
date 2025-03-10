import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json

from app.core.config import settings


# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Custom JSON Formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if hasattr(record, "method"):
            log_obj["method"] = record.method
        if hasattr(record, "process_time"):
            log_obj["process_time"] = record.process_time
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_logging():
    # Create logger
    logger = logging.getLogger(settings.PROJECT_NAME)
    logger.setLevel(logging.INFO)

    # JSON formatter
    json_formatter = JSONFormatter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File Handler for all logs
    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # File Handler for errors
    error_handler = TimedRotatingFileHandler(
        LOGS_DIR / "error.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    logger.addHandler(error_handler)

    # Set propagate to False to avoid duplicate logs
    logger.propagate = False

    return logger


# Create and export logger instance
logger = setup_logging() 