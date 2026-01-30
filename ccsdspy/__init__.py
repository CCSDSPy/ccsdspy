# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
IO Interface for Reading CCSDS Data in Python.
"""
import os.path
# For egg_info test builds to pass, put package imports here.

try:
    from ._version import __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown"
    version_tuple = (0, 0, "unknown version")

from .logger import _init_log
from .config import load_config, print_config

# Load user configuration
config = load_config()

log = _init_log(config=config)
log.info(f"CCSDSPy version {__version__} initialized.")

_package_directory = os.path.dirname(os.path.realpath(__file__))
_data_directory = os.path.join(_package_directory, "data")
_test_data_directory = os.path.join(_package_directory, "tests", "data")

from . import converters
from .packet_fields import PacketField, PacketArray
from .packet_types import FixedLength, VariableLength
from .utils import split_by_apid
