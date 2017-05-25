"""High level Object-Oriented interface methods for the package."""

_author__ = "Daniel da Silva <mail@danieldasilva.org>"

import numpy as np
from astropy.table import Table
from .decode import _decode_fixed_length


class PacketField(object):
    """A mnemonic contained inside a packet.    
    """
    
    def __init__(self, name, data_type, bit_length, bit_offset=None):
        """Define a new PacketField.
        
        Parameters
        ----------
        name : str
            String identifier for the field. This field species how you may
            call upon it later.
        data_type : {'uint', 'int', 'float', 'str', 'fill'}
            Data type of the field.
        bit_length : int
            Number of bits contained in the field
        bit_offset : int
            Bit offset into packet, including primary header.

        Raises
        ------
        TypeError
             If one of the arguments is not of the correct type.
        """
        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')
        if not isinstance(data_type, str):
            raise TypeError('data_type parameter must be a str')
        if not isinstance(bit_length, int):
            raise TypeError('bit_length parameter must be an int')
        if not (bit_offset is None or isinstance(bit_offset, int)):
            raise TypeError('bit_offset parameter must be an int')
        
        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length
        self._bit_offset = bit_offset

        
class FixedLength(object):
    """A packet definition used for decoding fixed-length byte-streams.   
    """
    
    def __init__(self, fields):
        """Define a fixed length packet.
        
        Parameters
        ----------
        fields : list of PacketField
            List of packet fields, holding the contents to decode.
        """
        self._fields = fields[:]

    def load(self, file):
        """Load a file containing this packet from disk.

        Parameters
        ----------
        file: str, file-like
           Path to file on the local file system, or file-like object to read from.

        Returns
        -------
        
        """
        file_bytes = np.fromfile(file, 'u1')
        field_arrays = _decode_fixed_length(file_bytes, self._fields)

        return Table(field_arrays.values(), names=field_arrays.keys())
