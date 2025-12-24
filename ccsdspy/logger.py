import logging
import sys
import json

from . import config as _config


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for log aggregation systems."""
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.msg,
            "module": record.module
        }
        return json.dumps(log_data)


def _init_log(config=None):
    if config is None:
        config = _config

    logger = logging.getLogger('ccsdspy')
    logger.setLevel(logging.DEBUG)
    log_level = level_str_to_level(config.get("logger", {}).get("log_level", "INFO"))
    log_format = config.get("logger", {}).get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_to_file = config.get("logger", {}).get("log_to_file", False)
    log_file_path = config.get("logger", {}).get("log_file_path", "ccsdspy.log")
    log_file_level = level_str_to_level(config.get("logger", {}).get("log_file_level", "DEBUG"))
    log_file_json = config.get("logger", {}).get("log_file_json", False)
    if log_to_file and not log_file_json:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(log_file_level)
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    elif log_to_file and log_file_json:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(log_file_level)
        formatter = JSONFormatter()
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger


def level_str_to_level(level_str):
    level_str = level_str.upper()
    if level_str == "CRITICAL":
        return logging.CRITICAL
    elif level_str == "ERROR":
        return logging.ERROR
    elif level_str == "WARNING":
        return logging.WARNING
    elif level_str == "INFO":
        return logging.INFO
    elif level_str == "DEBUG":
        return logging.DEBUG
    else:
        return logging.NOTSET