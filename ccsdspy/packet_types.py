"""High-level Object-oriented API for the different types of packets
(FixedLength and VariableLength) supported by the package.
"""

import csv
import os

import numpy as np

from .decode import _decode_fixed_length, _decode_variable_length
from .packet_fields import PacketField, PacketArray


__author__ = "Daniel da Silva <mail@danieldasilva.org>"


class _BasePacket:
    """Base class of FixedLength and VariableLength. Not to be instantiated
    directly.
    """

    def _init(self, fields):
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
        file : str
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


class FixedLength(_BasePacket):
    """Define a fixed length packet to decode binary data.

    Fixed length packets correspond to packats that are the same length and
    layout every time. A common example of this is housekeeping or status
    messages.
    """

    def __init__(self, fields):
        """
        Parameters
        ----------
        fields : list of :py:class:`~ccsdspy.PacketField` or :py:class:`~ccsdspy.PacketArray`
            Layout of packet fields contained in the definition.

        Raises
        ------
        ValueError
            one or more of the arguments are invalid
        """
        if any(field._bit_length == "expand" for field in fields):
            raise ValueError(
                "The FixedLength class does not support fields with "
                "bit_length='expand'. Instead, use the VariableLength "
                "class."
            )

        self._init(fields)

    def load(self, file, include_primary_header=False):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file : str
           Path to file on the local file system, or file-like object
        include_primary_header : bool
           If True, provides the primary header in the output

        Returns
        -------
        field_arrays : dict, string to NumPy array
            dictionary mapping field names to NumPy arrays, with key order matching
            the order of fields in the packet.
        """
        return _load(
            file,
            self._fields,
            "fixed_length",
            include_primary_header=include_primary_header,
        )


class VariableLength(_BasePacket):
    """Define a variable length packet to decode binary data.

    Variable length packets are packets which have a different length each
    time. Each variable length packet should have a single `PacketArray` with
    the `array_shape='expand'`, which will grow to fill the packet.

    Please note that while this class is able to parse fixed length packets, it
    is much slower. Use the :py:class:`~ccsdspy.FixedLength` class instead.

    Rules for variable length packets:
        - Do provide only one one expanding PacketArray with
          `array_shape='expand'`.
        - Do not specify the primary header fields manually
        - Do not specify explicit bit_offsets (they will be computed
         automatically)

    """

    def __init__(self, fields):
        """
        Parameters
        ----------
        fields : list of :py:class:`~ccsdspy.PacketField` or :py:class:`~ccsdspy.PacketArray`
            Layout of packet fields contained in the definition. No more than
            one field should have array_shape="expand". The field must have no
            bit_offset's. Do not include the primary header fields.

        Raises
        ------
        ValueError
            one or more of the arguments are invalid, or do not follow the
            specified rules.
        """
        expand_arrays = [
            field
            for field in fields
            if isinstance(field, PacketArray) and field._array_shape == "expand"
        ]

        if len(expand_arrays) > 1:
            raise ValueError(
                "The VariableLength class does not support more than one field "
                "with array_shape='expand', as the decoding process becomes "
                "ambiguous."
            )

        if not all(field._bit_offset is None for field in fields):
            raise ValueError(
                "The VariableLength class does not support explicit bit "
                "offsets. You must specify the entire packet so they can be "
                "determined automatically."
            )

        self._init(fields)

    def load(self, file, include_primary_header=False):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file : str
           Path to file on the local file system, or file-like object
        include_primary_header : bool
           If True, provides the primary header in the output

        Returns
        -------
        field_arrays : dict, string to NumPy array
            dictionary mapping field names to NumPy arrays, with key order matching
            the order of fields in the packet.
        """
        # The variable length decoder requires the full packet definition, so if
        # they didn't want the primary header fields, we parse for them and then
        # remove them after.
        packet_arrays = _load(
            file, self._fields, "variable_length", include_primary_header=True
        )

        if not include_primary_header:
            _delete_primary_header_fields(packet_arrays)

        return packet_arrays


def _delete_primary_header_fields(packet_arrays):
    """Modifies in place the packet arrays dictionary to delete primary
    header fields.

    Parameters
    -----------
    packet_arrays
        dictionary mapping field names to NumPy arrays, with key order matching
        the order fields in the packet. Modified in place
    """
    header_fields = _prepend_primary_header_fields([])

    for header_field in header_fields:
        del packet_arrays[header_field._name]


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
        if (
            existing_field._field_type != "array"
            or existing_field._array_shape == "expand"
        ):
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
    field_arrays : dict, str to numpy array
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
    existing_fields : list of `ccsdspy.PacketField`
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
    csv_file : str
        Path to file on the local file system

    Returns
    -------
    fields : list
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


def _load(file, fields, decoder_name, include_primary_header=False):
    """Decode a file-like object containing a sequence of these packets.

    Parameters
    ----------
    file: str
       Path to file on the local file system, or file-like object
    fields : list of `ccsdspy.PacketField`
       Layout of packet fields contained in the definition.
    decoder_name: {'fixed_length', 'variable_length'}
       String identifying which decoder to use.
    include_primary_header: bool
       If True, provides the primary header in the output

    Returns
    -------
    dictionary mapping field names to NumPy arrays, with key order matching
    the order fields in the packet.

    Raises
    ------
    ValueError
      the decoder_name is not one of the allowed values
    """
    if hasattr(file, "read"):
        file_bytes = np.frombuffer(file.read(), "u1")
    else:
        file_bytes = np.fromfile(file, "u1")

    if include_primary_header:
        fields = _prepend_primary_header_fields(fields)

    fields, expand_history = _expand_array_fields(fields)

    if decoder_name == "fixed_length":
        field_arrays = _decode_fixed_length(file_bytes, fields)
    elif decoder_name == "variable_length":
        field_arrays = _decode_variable_length(file_bytes, fields)
    else:
        raise ValueError(
            f"Invalid decoder_name 'f{decoder_name}' specified. Must be "
            "either 'fixed_length', or 'variable_length'"
        )

    field_arrays = _unexpand_field_arrays(field_arrays, expand_history)

    return field_arrays
