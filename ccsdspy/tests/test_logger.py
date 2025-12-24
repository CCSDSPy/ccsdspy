"""
Tests for the logging module
"""

import inspect
import logging
import os.path
import re


import pytest

from ccsdspy import config, log
from ccsdspy.logger import level_str_to_level


def test_logger_name():
    assert log.name == "ccsdspy"


def test_is_the_logger_there():
    assert isinstance(log, logging.Logger)


def test_is_level_configed():
    """
    Test to make sure that the logger follows the config:

    log_level
    """
    config_level_numeric = level_str_to_level(config.get("logger")["log_level"])
    assert log.getEffectiveLevel() == config_level_numeric


def test_is_log_to_file_configed():
    """
    Test to make sure that the logger follows the config:

    log_to_file, log_file_level, log_file_path
    """

    if config["logger"]["log_file_level"] == "True":
        #  there must be two handlers, one streaming and one to file.
        assert len(log.handlers) == 2
        #  one of the handlers must be FileHandler
        assert isinstance(log.handlers[0], logging.FileHandler) or isinstance(
            log.handlers[1], logging.FileHandler
        )
        fh = None
        if isinstance(log.handlers[0], logging.FileHandler):
            fh = log.handlers[0]

        if isinstance(log.handlers[1], logging.FileHandler):
            fh = log.handlers[1]

        if fh is not None:
            log_file_level_str = config.get("logger", "log_file_level")
            assert level_str_to_level(log_file_level_str) == fh.level

            log_file_path = config.get("logger", "log_file_path")
            assert os.path.basename(fh.baseFilename) == os.path.basename(log_file_path)


def send_to_log(message, kind="INFO"):
    """
    A simple function to demonstrate the logger generating an origin.
    """
    if kind.lower() == "info":
        log.info(message)
    elif kind.lower() == "debug":
        log.debug(message)


def test_log_format_real_output(caplog):
    """
    Test that when logging something, the output string has the expected format.
    This tests the actual string formatting rather than just the presence of attributes.
    """
    log.info("Testing log format")
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"

    entry = caplog.records[0]
    # Check timestamp format: YYYY-MM-DD HH:MM:SS,SSS
    assert hasattr(entry, "asctime")
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}", entry.asctime)

    # Check level name
    assert hasattr(entry, "levelname")
    assert entry.levelname == "INFO"

    # Check message
    assert hasattr(entry, "message")
    assert entry.message == "Testing log format"
