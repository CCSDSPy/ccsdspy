"""High level Object-Oriented interface methods for the package."""

_author__ = "Daniel da Silva <mail@danieldasilva.org>"

import numpy as np
from astropy.table import Table
from .decode import _decode_fixed_length


class PacketField(object):
    """A field contained in a packet.
    """
    
    def __init__(self, name, data_type, bit_length, bit_offset=None):
        """Define a new PacketField.
        
        Parameters
        ----------
        name : str
            String identifier for the field. The name specified how you may
            call upon this data later.
        data_type : {'uint', 'int', 'float', 'str', 'fill'}
            Data type of the field.
        bit_length : int
            Number of bits contained in the field.
        bit_offset : int, optional
            Bit offset into packet, including primary header. If this is not
            specified, than the bit offset will the be calculated automatically
            from its position inside the packet definition.

        Raises
        ------
        TypeError
             If one of the arguments is not of the correct type.
        ValueError
             data type is invalid
        """
        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')
        if not isinstance(data_type, str):
            raise TypeError('data_type parameter must be a str')
        if not isinstance(bit_length, int):
            raise TypeError('bit_length parameter must be an int')
        if not (bit_offset is None or isinstance(bit_offset, int)):
            raise TypeError('bit_offset parameter must be an int')

        valid_data_types = ('uint', 'int', 'float', 'str', 'fill')
        if not data_type in valid_data_types:
            raise ValueError('data_type must be one of {valids}'.format(
                valids=repr(valid_data_types)))
            
        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length
        self._bit_offset = bit_offset

        
class FixedLength(object):
    """Define a fixed length packet to decode byte sequences.

    In the context of engineering and science, fixed length packets correspond
    to data that is of the same layout every time. Examples of this include
    sensor time series, status codes, or error messages.
    """    
    def __init__(self, fields):
        """        
        Parameters
        ----------
        fields : list of `ccsdspy.PacketField`
            Layout of packet fields contained in the definition.
        """
        self._fields = fields[:]

    def load(self, file):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file: str, file-like
           Path to file on the local file system, or file-like object (such
           as `StringIO.StringIO`)

        Returns
        -------
        `astropy.table.Table` containing one column for each field
        """
        file_bytes = np.fromfile(file, 'u1')
        field_arrays = _decode_fixed_length(file_bytes, self._fields)

        table = Table(field_arrays.values(), names=field_arrays.keys())

        return table
