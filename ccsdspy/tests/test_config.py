"""
Tests for the config module
"""

import os


import ccsdspy
from ccsdspy.config import (
    _is_writable_dir,
)

USER = os.path.expanduser("~")


def test_is_writable_dir(tmpdir, tmp_path):
    """
    Test the _is_writable_dir function.
    """
    assert _is_writable_dir(tmpdir)
    tmp_file = tmpdir.join("hello.txt")
    # Have to write to the file otherwise its seen as a directory(?!)
    tmp_file.write("content")
    # Checks directory with a file
    assert _is_writable_dir(tmpdir)
    # Checks a filepath instead of directory
    assert not _is_writable_dir(tmp_file)


def test_print_config(capsys):
    """
    Test the print_config function.
    """
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
