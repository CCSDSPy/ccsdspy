"""High level Object-Oriented interface methods for the package."""

_author__ = "Daniel da Silva <mail@danieldasilva.org>"

import numpy as np
from .decode import _decode_fixed_length


class PacketField(object):
    """A mnemonic contained inside a packet.    
    """
    
    def __init__(self, name, data_type, bit_length):
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

        Raises
        ------
        ValueError
             If one of the arguments is not of the correct type.
        """
        if not isinstance(name, str):
            raise ValueError('name parameter must be a str')
        if not isinstance(data_type, str):
            raise ValueError('data_type parameter must be a str')
        if not isinstance(bit_length, int):
            raise ValueError('bit_length parameter must be an int')
        
        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length

        
class PacketDefinition(object):
    """A packet definition used for decoding byte-streams.   
    """
    
    def __init__(self, fields):
        """Define a fixed length packet.
        
        Parameters
        ----------
        fields : list of PacketField
            List of packet fields, holding the contents to decode.
        
        Raises
        ------
        ValueError
             The parameter was not a list of PacketField's.
        """        
        self._fields = fields[:]

        
class FixedLength(object):
    """Represents a Fixed-Length CCSDS file on the file-system."""

    def __init__(self, file_, packet_def):
        """Create a FixedLength objected.
        
        Parameters
        ----------
        file_: str, file-like
           Path to file on the local file system, or file-like object to read from.
        packet_def: FixedLengthPacket
           Description of data inside the packet.
        """    
        file_bytes = np.fromfile(file_, 'u1')

        self._field_arrays = _decode_fixed_length(file_bytes, packet_def._fields)

    def keys(self):
        return self._field_arrays.keys()
        
    def __getitem__(self, key):
        return self._field_arrays[key]
