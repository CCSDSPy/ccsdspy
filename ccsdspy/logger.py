import logging
import json
from contextlib import contextmanager

from . import config as _config


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for log aggregation systems."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.msg,
            "module": record.module,
        }
        return json.dumps(log_data)


class CCSDSpyLogger(logging.Logger):
    """
    This class is used to set up a custom logger.

    The main functionality added by this class over the built-in
    logging.Logger class is the ability to add two context managers that
    temporarily log messages to a file or to a list.

    This class is adapted from the `AstropyLogger <https://docs.astropy.org/en/stable/api/astropy.logger.AstropyLogger.html#astropy.logger.AstropyLogger>`_ class in the Astropy
    project (https://www.astropy.org/). The original class is licensed
    under the BSD 3-Clause license.
    """

    @contextmanager
    def log_to_file(self, filename, filter_level=None, filter_origin=None):
        """
        Context manager to temporarily log messages to a file.

        Parameters
        ----------
        filename : str
            The file to log messages to.
        filter_level : str
            If set, any log messages less important than ``filter_level`` will
            not be output to the file. Note that this is in addition to the
            top-level filtering for the logger, so if the logger has level
            'INFO', then setting ``filter_level`` to ``INFO`` or ``DEBUG``
            will have no effect, since these messages are already filtered
            out.
        filter_origin : str
            If set, only log messages with an origin starting with
            ``filter_origin`` will be output to the file.
        Notes
        -----
        By default, the logger already outputs log messages to a file set in
        the configuration file. Using this context manager does not
        stop log messages from being output to that file, nor does it stop log
        messages from being printed to standard output.

        Examples
        --------
        The context manager is used as::

            with logger.log_to_file('myfile.log'):
                # your code here
        """
        fh = logging.FileHandler(filename)
        if filter_level is not None:
            fh.setLevel(filter_level)
        if filter_origin is not None:
            fh.addFilter(FilterOrigin(filter_origin))
        log_file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        f = logging.Formatter(log_file_format)
        fh.setFormatter(f)
        self.addHandler(fh)
        yield
        fh.close()
        self.removeHandler(fh)

    @contextmanager
    def log_to_list(self, filter_level=None, filter_origin=None):
        """
        Context manager to temporarily log messages to a list.

        Parameters
        ----------
        filename : str
            The file to log messages to.
        filter_level : str
            If set, any log messages less important than ``filter_level`` will
            not be output to the file. Note that this is in addition to the
            top-level filtering for the logger, so if the logger has level
            'INFO', then setting ``filter_level`` to ``INFO`` or ``DEBUG``
            will have no effect, since these messages are already filtered
            out.
        filter_origin : str
            If set, only log messages with an origin starting with
            ``filter_origin`` will be output to the file.

        Notes
        -----
        Using this context manager does not stop log messages from being
        output to standard output.

        Examples
        --------
        The context manager is used as::

            with logger.log_to_list() as log_list:
                # your code here
        """
        lh = ListHandler()
        if filter_level is not None:
            lh.setLevel(filter_level)
        if filter_origin is not None:
            lh.addFilter(FilterOrigin(filter_origin))
        self.addHandler(lh)
        yield lh.log_list
        self.removeHandler(lh)


class FilterOrigin:
    """A filter for the record origin."""

    def __init__(self, origin):
        self.origin = origin

    def filter(self, record):
        return record.origin.startswith(self.origin)


class ListHandler(logging.Handler):
    """A handler that can be used to capture the records in a list."""

    def __init__(self, filter_level=None, filter_origin=None):
        logging.Handler.__init__(self)
        self.log_list = []

    def emit(self, record):
        self.log_list.append(record)


def _init_log(config=None):
    if config is None:
        config = _config

    logger = logging.getLoggerClass()
    logging.setLoggerClass(CCSDSpyLogger)
    logger = logging.getLogger("ccsdspy")
    logger.setLevel(logging.DEBUG)
    log_level = level_str_to_level(config.get("logger", {}).get("log_level", "INFO"))
    log_format = config.get("logger", {}).get(
        "log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_to_file = config.get("logger", {}).get("log_to_file", False)
    log_file_path = config.get("logger", {}).get("log_file_path", "ccsdspy.log")
    log_file_level = level_str_to_level(config.get("logger", {}).get("log_file_level", "DEBUG"))
    log_file_json = config.get("logger", {}).get("log_file_json", False)
    log_file_format = config.get("logger", {}).get(
        "log_file_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log_time_format = config.get("general", {}).get("time_format", "%Y-%m-%d %H:%M:%S")
    if log_to_file and not log_file_json:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(log_file_level)
        formatter = logging.Formatter(log_file_format, datefmt=log_time_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    elif log_to_file and log_file_json:
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(log_file_level)
        formatter = JSONFormatter(datefmt=log_time_format)
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
