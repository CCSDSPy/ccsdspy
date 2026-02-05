"""
Tests for the config module
"""

import os

import pytest

import ccsdspy
from ccsdspy.config import (
    load_config,
    copy_default_config,
    _is_writable_dir,
    _get_user_configdir,
)

USER = os.path.expanduser("~")


def test_create_config(tmpdir, monkeypatch):
    """Tests creating a configuration directory."""
    monkeypatch.setenv("ccsdspy_CONFIGDIR", tmpdir)
    copy_default_config()
    config = load_config()

    assert isinstance(config, dict)
    assert "general" in config
    assert "logger" in config


def test_copy_default_config_overwriting(tmpdir, monkeypatch):
    """Tests the overwrite=False keyword with copy_default_config()"""
    monkeypatch.setenv("ccsdspy_CONFIGDIR", tmpdir)
    copy_default_config()

    # Test overwrite=False issues warning
    with pytest.warns(UserWarning):
        copy_default_config(overwrite=False)

    # Test overwrite=True issues warning and makes backup
    with pytest.warns(UserWarning):
        copy_default_config(overwrite=True)

    bak_file = os.path.join(tmpdir, "config.yml.bak")
    assert os.path.exists(bak_file)

    # Test loading config
    config = load_config()

    assert isinstance(config, dict)
    assert "general" in config
    assert "logger" in config


def test_load_config_path_does_not_exist(monkeypatch, tmpdir):
    """Tests loading a config where the config path does not exist."""
    monkeypatch.setenv("ccsdspy_CONFIGDIR", tmpdir)
    config = load_config()
    assert isinstance(config, dict)


def test_is_writable_dir(tmpdir, tmp_path):
    """Test the _is_writable_dir function."""
    assert _is_writable_dir(tmpdir)
    tmp_file = tmpdir.join("hello.txt")
    # Have to write to the file otherwise its seen as a directory(?!)
    tmp_file.write("content")
    # Checks directory with a file
    assert _is_writable_dir(tmpdir)
    # Checks a filepath instead of directory
    assert not _is_writable_dir(tmp_file)


def test_get_user_configdir_not_writable(monkeypatch, tmpdir):
    """Tests the _get_user_configdir() function with a directory that's
    not writable.
    """
    monkeypatch.setenv("ccsdspy_CONFIGDIR", tmpdir)
    os.chmod(tmpdir, 0o111)

    try:
        with pytest.raises(RuntimeError):
            _get_user_configdir()

    finally:
        # don't mess up pytest's ability to delete the tmpdir
        os.chmod(tmpdir, 0x700)


def test_print_config(capsys):
    """Test the print_config function."""
    # Run the functio to print the config
    ccsdspy.print_config()
    # Capture the output
    captured = capsys.readouterr()
    assert isinstance(captured.out, str)
    # assert general section
    assert "[general]" in captured.out
    # assert mission data
    # assert logger
    assert "[logger]" in captured.out
