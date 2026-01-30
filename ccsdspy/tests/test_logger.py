"""
Tests for the logging module
"""

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


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARN", "ERROR"])
def test_log_to_list(level):
    orig_level = log.level

    try:
        if level is not None:
            log.setLevel(level)

        with log.log_to_list() as log_list:
            log.error("Error message")
            log.warning("Warning message")
            log.info("Information message")
            log.debug("Debug message")
    finally:
        log.setLevel(orig_level)

    if level is None:
        # The log level *should* be set to whatever it was in the config
        level = config.log_level

    # Check list length
    if level == "DEBUG":
        assert len(log_list) == 4
    elif level == "INFO":
        assert len(log_list) == 3
    elif level == "WARN":
        assert len(log_list) == 2
    elif level == "ERROR":
        assert len(log_list) == 1

    # Check list content

    assert log_list[0].levelname == "ERROR"
    assert log_list[0].message.startswith("Error message")

    if len(log_list) >= 2:
        assert log_list[1].levelname == "WARNING"
        assert log_list[1].message.startswith("Warning message")

    if len(log_list) >= 3:
        assert log_list[2].levelname == "INFO"
        assert log_list[2].message.startswith("Information message")

    if len(log_list) >= 4:
        assert log_list[3].levelname == "DEBUG"
        assert log_list[3].message.startswith("Debug message")


def test_log_to_list_level():
    with log.log_to_list(filter_level="ERROR") as log_list:
        log.error("Error message")
        log.warning("Warning message")

    assert len(log_list) == 1 and log_list[0].levelname == "ERROR"


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARN", "ERROR"])
def test_log_to_file(tmp_path, level):
    local_path = tmp_path / "test.log"
    log_file = local_path.open("wb")
    log_path = str(local_path.resolve())
    orig_level = log.level

    try:
        if level is not None:
            log.setLevel(level)

        with log.log_to_file(log_path):
            log.error("Error message")
            log.warning("Warning message")
            log.info("Information message")
            log.debug("Debug message")

        log_file.close()
    finally:
        log.setLevel(orig_level)

    log_file = local_path.open("r")
    log_entries = log_file.readlines()
    log_file.close()

    if level is None:
        # The log level *should* be set to whatever it was in the config
        level = config.log_level

    # Check list length
    if level == "DEBUG":
        assert len(log_entries) == 4
    elif level == "INFO":
        assert len(log_entries) == 3
    elif level == "WARN":
        assert len(log_entries) == 2
    elif level == "ERROR":
        assert len(log_entries) == 1

    # Check list content

    print(log_entries)
    assert log_entries[0].split(" - ")[-1].strip() == "Error message"

    if len(log_entries) >= 2:
        assert log_entries[1].split(" - ")[-1].strip() == "Warning message"

    if len(log_entries) >= 3:
        assert log_entries[2].split(" - ")[-1].strip() == "Information message"

    if len(log_entries) >= 4:
        assert log_entries[3].split(" - ")[-1].strip() == "Debug message"


def test_log_to_file_level(tmp_path):
    local_path = tmp_path / "test.log"
    log_file = local_path.open("wb")
    log_path = str(local_path.resolve())

    with log.log_to_file(log_path, filter_level="ERROR"):
        log.error("Error message")
        log.warning("Warning message")

    log_file.close()

    log_file = local_path.open("r")
    log_entries = log_file.readlines()
    log_file.close()

    assert len(log_entries) == 1
    assert log_entries[0].split(" - ")[-1].strip() == "Error message"
