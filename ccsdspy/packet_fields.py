"""High level object-oriented API for elements that can exist in a packet.

See also:
- packet_types.FixedLength
- packet_types.VariableLength
"""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"

import numpy as np


class PacketField:
    """A field contained in a packet."""

    def __init__(self, name, data_type, bit_length, bit_offset=None, byte_order="big"):
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
            Bit offset into packet, including the primary header which is 48 bits long.
            If this is not specified, than the bit offset will the be calculated automatically
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
            raise TypeError("name parameter must be a str")
        if not isinstance(data_type, str):
            raise TypeError("data_type parameter must be a str")
        if not isinstance(bit_length, (int, np.integer)):
            raise TypeError("bit_length parameter must be an int")
        if not (bit_offset is None or isinstance(bit_offset, (int, np.integer))):
            raise TypeError("bit_offset parameter must be an int")

        valid_data_types = ("uint", "int", "float", "str", "fill")
        if data_type not in valid_data_types:
            raise ValueError(f"data_type must be one of {valid_data_types}")

        valid_byte_orders = ("big", "little")
        if byte_order not in valid_byte_orders:
            raise ValueError(f"byte_order must be one of {valid_byte_orders}")

        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length
        self._bit_offset = bit_offset
        self._byte_order = byte_order

        self._field_type = "element"
        self._array_shape = None
        self._array_order = None

    def __repr__(self):
        values = {k: repr(v) for (k, v) in self.__dict__.items()}

        return (
            "PacketField(name={_name}, data_type={_data_type}, "
            "bit_length={_bit_length}, bit_offset={_bit_offset}, "
            "byte_order={_byte_order})".format(**values)
        )

    def __iter__(self):
        return iter(
            [
                ("name", self._name),
                ("dataType", self._data_type),
                ("bitLength", self._bit_length),
                ("bitOffset", self._bit_offset),
                ("byteOrder", self._byte_order),
            ]
        )


class PacketArray(PacketField):
    """An array contained in a packet, similar to :py:class:`~ccsdspy.PacketField` but with multiple
    elements of the same size (e.g. image).
    """

    def __init__(self, *args, array_shape=None, array_order="C", **kwargs):
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
        array_shape : int, tuple of ints, or 'expand'
            Shape of the array as a tuple. For a 1-dimensional array, a single integer
            can be supplied. For details on expanding arrays, see the :py:class:`~ccsdspy.VariableLength`
            class.
        array_order  {'C', 'F'}
            Row-major (C-style) or column-major (Fortran-style) order.
        bit_offset : int, optional
            Bit offset into packet, including the primary header which is 48 bits long.
            If this is not specified, than the bit offset will the be calculated automatically
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
        if array_shape == "expand":
            if kwargs["data_type"] is None:
                kwargs["data_type"] = "uint"
            elif kwargs["data_type"] != "uint":
                raise ValueError("Expanding arrays must be data_type='uint'")
        else:
            if isinstance(array_shape, int):
                array_shape = (array_shape,)
            if not isinstance(array_shape, tuple):
                raise TypeError("array_shape parameter must be a tuple of ints")
            if not all(isinstance(dim, int) for dim in array_shape):
                raise TypeError("array_shape parameter must be a tuple of ints")

            if not all(dim >= 0 for dim in array_shape):
                raise TypeError("array_shape parameter dimensions must be >= 0")
            if sum(array_shape) == 0:
                raise TypeError("array must have at least one element")

        if not isinstance(array_order, str):
            raise TypeError("array_order parameter must be string")
        if array_order not in {"C", "F"}:
            raise TypeError("array_order parameter must be either 'C' or 'F'")

        super().__init__(*args, **kwargs)
        self._field_type = "array"
        self._array_shape = array_shape
        self._array_order = array_order
