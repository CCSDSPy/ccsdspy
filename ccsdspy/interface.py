"""High level Object-Oriented interface methods for the package."""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"
import os.path
import csv

import numpy as np

from .decode import _decode_fixed_length


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

        self._field_type = "element"
        self._name = name
        self._data_type = data_type
        self._bit_length = bit_length
        self._bit_offset = bit_offset
        self._byte_order = byte_order

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
    """An array contained in a packet, similar to PacketField but with multiple
    elements.
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
        array_shape: int or tuple of ints
            Shape of the array as a tuple. For a 1-dimensional array, a single integer
            can be supplied
        array_order: {'C', 'F'}
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
        super().__init__(*args, **kwargs)

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

        self._field_type = "array"
        self._array_shape = array_shape
        self._array_order = array_order


class FixedLength:
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

    @classmethod
    def from_file(cls, file):
        """
        Parameters
        ----------
        file: str
           Path to file on the local file system that defines the packet fields.
           Currently only suports csv files.  See :download:`simple_csv_3col.csv <../../ccsdspy/tests/data/packet_def/simple_csv_3col.csv>`
           and :download:`simple_csv_4col.csv <../../ccsdspy/tests/data/packet_def/simple_csv_4col.csv>`

        Returns
        -------
        An instance of FixedLength.
        """
        file_extension = os.path.splitext(file)
        if file_extension[1] == ".csv":
            fields = _get_fields_csv_file(file)
        else:
            raise ValueError(f"File type {file_extension[1]} not supported.")

        return cls(fields)

    def load(self, file, include_primary_header=False):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file: str
           Path to file on the local file system, or file-like object
        include_primary_header: bool
           If True, provides the primary header in the output

        Returns
        -------
        dictionary mapping field names to NumPy arrays, with key order matching
        the order fields in the packet.
        """
        if hasattr(file, "read"):
            file_bytes = np.frombuffer(file.read(), "u1")
        else:
            file_bytes = np.fromfile(file, "u1")

        fields = self._fields.copy()  # copy references to new list to be safe

        if include_primary_header:
            fields = _prepend_primary_header_fields(fields)

        fields, expand_history = _expand_array_fields(fields)

        field_arrays = _decode_fixed_length(file_bytes, fields)

        field_arrays = _unexpand_field_arrays(field_arrays, expand_history)

        return field_arrays


def _expand_array_fields(existing_fields):
    """Expand arrays into multiple fields, one for each element.

    Returns a new list of fields as well as a data structure which can be used
    to reverse this process. See the `_unexpand_field_arrays()` function to reverse
    this process.

    Parameters
    ----------
    existing_fields : list of `ccsdspy.PacketField`
      Layout of packet fields contained in the definition, with PacketArray

    Returns
    -------
    return_fields : list of `ccsdspy.PacketField`
      Layout of packet fields contained in the definition, without PacketArray's
    expand_history : dict
      Dictionary mapping array name with shape/data-type and field expansions
    """
    return_fields = []
    expand_history = {}

    for existing_field in existing_fields:
        if existing_field._field_type != "array":
            return_fields.append(existing_field)
            continue

        array_shape = existing_field._array_shape
        array_order = existing_field._array_order

        index_vecs = [np.arange(dim) for dim in array_shape]
        index_grids = np.meshgrid(*index_vecs, indexing="ij")
        indeces_flat = [
            index_grid.flatten(order=array_order) for index_grid in index_grids
        ]

        expand_history[existing_field._name] = {
            "shape": array_shape,
            "data_type": existing_field._data_type,
            "fields": {},
        }

        for i, indeces in enumerate(zip(*indeces_flat)):
            name = f"{existing_field._name}[{','.join(map(str,indeces))}]"
            if existing_field._bit_offset is None:
                bit_offset = None
            else:
                bit_offset = existing_field._bit_offset + i * existing_field._bit_length

            return_field = PacketField(
                name=name,
                data_type=existing_field._data_type,
                bit_length=existing_field._bit_length,
                bit_offset=bit_offset,
                byte_order=existing_field._byte_order,
            )

            expand_history[existing_field._name]["fields"][name] = indeces
            return_fields.append(return_field)

    return return_fields, expand_history


def _unexpand_field_arrays(field_arrays, expand_history):
    """Reverse the array expansion process from `_expand_array_fields`.

    Parameters
    ----------
    field_arrays : dict, str to array
      Dictionary mapping field names to NumPy arrays, with key order matching
      the order fields in the packet. Has a key for each array element.
    expand_history : dict
      Dictionary mapping array name with shape/data-type and field expansions

    Returns
    -------
    return_field_arrays : dict, str to array
      Dictionary mapping field names to NumPy arrays, with key order matching
      the order fields in the packet. Has keys mapping to full arrays.
    """
    npackets = list(field_arrays.values())[0].shape[0]
    return_field_arrays = field_arrays.copy()

    for array_name, array_details in expand_history.items():
        array_shape = (npackets,) + array_details["shape"]
        array_dtype = field_arrays[list(array_details["fields"].keys())[0]].dtype
        array = np.zeros(array_shape, dtype=array_dtype)

        for element_name, indeces in array_details["fields"].items():
            array.__setitem__((slice(None),) + indeces, field_arrays[element_name])
            del return_field_arrays[element_name]

        return_field_arrays[array_name] = array

    return return_field_arrays


def _prepend_primary_header_fields(existing_fields):
    """Helper function that prepends primary header fields to a list of packet
    fields, to support load(include_primary_header=True)

    Parameters
    ----------
    existing_fields: list of `ccsdspy.PacketField`
      Non-primary header fields defined by the packet.

    Returns
    -------
    New list of fields with the primary header fields prepended.
    """
    return_fields = [
        PacketField(
            name="CCSDS_VERSION_NUMBER",
            data_type="uint",
            bit_length=3,
            bit_offset=0,
        ),
        PacketField(
            name="CCSDS_PACKET_TYPE",
            data_type="uint",
            bit_length=1,
            bit_offset=3,
        ),
        PacketField(
            name="CCSDS_SECONDARY_FLAG",
            data_type="uint",
            bit_length=1,
            bit_offset=4,
        ),
        PacketField(name="CCSDS_APID", data_type="uint", bit_length=11, bit_offset=5),
        PacketField(
            name="CCSDS_SEQUENCE_FLAG",
            data_type="uint",
            bit_length=2,
            bit_offset=16,
        ),
        PacketField(
            name="CCSDS_SEQUENCE_COUNT",
            data_type="uint",
            bit_length=14,
            bit_offset=18,
        ),
        PacketField(
            name="CCSDS_PACKET_LENGTH",
            data_type="uint",
            bit_length=16,
            bit_offset=32,
        ),
    ]

    return_fields.extend(existing_fields)

    return return_fields


def _get_fields_csv_file(csv_file):
    """Parse a simple comma-delimited file that defines a packet.

    Should not include the CCSDS header. The minimum set of columns are (name,
    data_type, bit_length). An optional bit_offset can also be provided.

    Parameters
    ----------
    csv_file: str
        Path to file on the local file system

    Returns
    -------
    fields: list
        A list of `PacketField` objects.
    """
    req_columns = ["name", "data_type", "bit_length"]

    with open(csv_file, "r") as fp:
        fields = []
        reader = csv.DictReader(fp, skipinitialspace=True)
        headers = reader.fieldnames

        if headers is None:
            raise RuntimeError("CSV file must not be empty")

        if not all((req_col in headers) for req_col in req_columns):
            raise ValueError(f"Minimum required columns are {req_columns}.")

        for row in reader:  # skip the header row
            if "bit_offset" not in headers:  # 3 col csv file
                fields.append(
                    PacketField(
                        name=row["name"],
                        data_type=row["data_type"],
                        bit_length=int(row["bit_length"]),
                    )
                )
            if "bit_offset" in headers:  # 4 col csv file provides bit offsets
                # TODO: Check the consistency of bit_offsets versus previous bit_lengths
                fields.append(
                    PacketField(
                        name=row["name"],
                        data_type=row["data_type"],
                        bit_length=int(row["bit_length"]),
                        bit_offset=int(row["bit_offset"]),
                    )
                )

    return fields
