"""High level Object-Oriented interface methods for the package."""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"

import numpy as np

from .decode import _decode_fixed_length


class PacketField(object):
    """A field contained in a packet.
    """
    
    def __init__(self, name, data_type, bit_length, bit_offset=None,
                 byte_order='big'):
        """
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
        byte_order : {'big', 'little'}, optional
            Byte order of the field. Defaults to big endian.

        Raises
        ------
        TypeError
             If one of the arguments is not of the correct type.
        ValueError
             data_type or byte_order is invalid
        """
        if not isinstance(name, str):
            raise TypeError('name parameter must be a str')
        if not isinstance(data_type, str):
            raise TypeError('data_type parameter must be a str')
        if not isinstance(bit_length, (int, np.integer)):
            raise TypeError('bit_length parameter must be an int')
        if not (bit_offset is None or isinstance(bit_offset, (int, np.integer))):
            raise TypeError('bit_offset parameter must be an int')
        
        valid_data_types = ('uint', 'int', 'float', 'str', 'fill')
        if data_type not in valid_data_types:
            raise ValueError('data_type must be one of {valids}'.format(
                valids=repr(valid_data_types)))

        valid_byte_orders = ('big', 'little')
        if byte_order not in valid_byte_orders:
            raise ValueError('byte_order must be one of {valids}'.format(
                valids=repr(valid_byte_orders)))        
        
        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length
        self._bit_offset = bit_offset
        self._byte_order = byte_order

    def __repr__(self):
        values = {k: repr(v) for (k, v) in self.__dict__.items()}

        return ('PacketField(name={_name}, data_type={_data_type}, '
                'bit_length={_bit_length}, bit_offset={_bit_offset}, '
                'byte_order={_byte_order})'.format(**values))

    def __iter__(self):
        return iter([('name', self._name), ('dataType', self._data_type), ('bitLength', self._bit_length), ('bitOffset', self._bit_offset), ('byteOrder', self._byte_order)])

                
class FixedLength(object):
    """Define a fixed length packet to decode binary data.

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
        file: str
           Path to file on the local file system, or file-like object

        Returns
        -------
        dictionary mapping field names to NumPy arrays, with key order matching
        the order fields in the packet.
        """
        if hasattr(file, 'read'):
            file_bytes = np.frombuffer(file.read(), 'u1')
        else:
            file_bytes = np.fromfile(file, 'u1')

        field_arrays = _decode_fixed_length(file_bytes, self._fields)
        return field_arrays
