"""
This module provides configuration file functionality.

This code is based on that provided by SunPy see
    licenses/SUNPY.rst
"""

from json import load
import os
import shutil
import yaml
from pathlib import Path
import warnings

from appdirs import AppDirs

import ccsdspy

__all__ = ["load_config", "copy_default_config", "print_config", "CONFIG_DIR"]

# We use AppDirs to locate and create the config directory.
dirs = AppDirs("ccsdspy", "ccsdspy")
# Default one set by AppDirs
CONFIG_DIR = dirs.user_config_dir
CACHE_DIR = dirs.user_cache_dir


def load_config():
    """
    Load and read the configuration file.

    If a configuration file does not exist in the user's home directory,
    it will read in the defaults from the package's data directory.

    The selected configuration can be overridden by setting the `ccsdspy_CONFIGDIR`
    environment variable. This environment variable will take precedence
    over the mission specified in the configuration file.

    Returns
    -------
    config : dict
        The loaded configuration data, as a dictionary.
    """
    config_path = Path(_get_user_configdir()) / "config.yml"
    if not config_path.exists():
        config_path = Path(ccsdspy.__file__).parent / "data" / "config.yml"

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


def _get_user_configdir():
    """
    Return the configuration directory path.

    The configuration directory is determined by the "ccsdspy_CONFIGDIR"
    environment variable or a default directory set by the application.

    Returns
    -------
    str: The path to the configuration directory.

    Raises
    ------
    RuntimeError: If the configuration directory is not writable.
    """
    configdir = os.environ.get("ccsdspy_CONFIGDIR", CONFIG_DIR)
    if not _is_writable_dir(configdir):
        raise RuntimeError(f'Could not write to ccsdspy_CONFIGDIR="{configdir}"')
    return configdir


def _is_writable_dir(path):
    """
    Check if the specified path is a writable directory.

    Parameters
    ----------
    path: str or Path
        The path to check.

    Returns
    -------
    bool: True if the path is a writable directory, False otherwise.

    Raises
    ------
    FileExistsError: If a file exists at the path instead of a directory.
    """
    # Worried about multiple threads creating the directory at the same time.
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except FileExistsError:  # raised if there's an existing file instead of a directory
        return False
    else:
        return Path(path).is_dir() and os.access(path, os.W_OK)


def copy_default_config(overwrite=False):
    """
    Copy the default configuration file to the user's configuration directory.

    If the configuration file already exists, it will be overwritten if the
    `overwrite` parameter is set to True.

    Parameters
    ----------
    overwrite : bool
         Whether to overwrite an existing configuration file.

    Raises
    ------
    RuntimeError: If the configuration directory is not writable.
    """
    config_filename = "config.yml"
    config_file = Path(ccsdspy.__file__).parent / "data" / config_filename

    # Note: get_user_configdir() ensures directory is writable
    user_config_dir = Path(_get_user_configdir())
    user_config_file = user_config_dir / config_filename

    if user_config_file.exists():
        if overwrite:
            message = (
                "User config file already exists. "
                "This will be overwritten with a backup written in the same location."
            )
            warnings.warn(message)
            os.rename(str(user_config_file), str(user_config_file) + ".bak")
            shutil.copyfile(config_file, user_config_file)
        else:
            message = (
                "User config file already exists. "
                "To overwrite it use `copy_default_config(overwrite=True)`"
            )
            warnings.warn(message)
    else:
        shutil.copyfile(config_file, user_config_file)


def print_config():
    """
    Print the current configuration options.
    """
    config = load_config()
    print("FILES USED:")
    for file_ in _find_config_files():
        print("  " + file_)

    print("\nCONFIGURATION:")
    for section, settings in config.items():
        if isinstance(settings, dict):  # Nested configuration
            print(f"  [{section}]")
            for option, value in settings.items():
                print(f"  {option} = {value}")
            print("")
        else:  # Not a nested configuration
            print(f"  {section} = {settings}")


def _find_config_files():
    """
    Find the locations of configuration files.

    Returns
    -------
    list: A list of paths to the configuration files.
    """
    config_files = []
    config_filename = "config.yml"

    # find default configuration file
    module_dir = Path(ccsdspy.__file__).parent
    config_files.append(str(module_dir / "data" / config_filename))

    # if a user configuration file exists, add that to list of files to read
    # so that any values set there will override ones specified in the default
    # config file
    config_path = Path(_get_user_configdir())
    if config_path.joinpath(config_filename).exists():
        config_files.append(str(config_path.joinpath(config_filename)))

    return config_files
