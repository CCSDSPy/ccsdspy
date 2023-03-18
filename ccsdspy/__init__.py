# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
IO Interface for Reading CCSDS Data in Python.
"""

# For egg_info test builds to pass, put package imports here.

from . import converters
from .packet_fields import PacketField, PacketArray
from .packet_types import FixedLength, VariableLength
from .utils import split_by_apid

try:
    from ._version import __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown"
    version_tuple = (0, 0, "unknown version")
