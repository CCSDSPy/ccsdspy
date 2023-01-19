# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
IO Interface for Reading CCSDS Data in Python.
"""

# For egg_info test builds to pass, put package imports here.

from .packet_fields import PacketField, PacketArray
from .packet_types import FixedLength, VariableLength
from .utils import split_by_apid
