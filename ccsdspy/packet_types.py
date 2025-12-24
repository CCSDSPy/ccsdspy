"""High-level Object-oriented API for the different types of packets
(FixedLength and VariableLength) supported by the package.
"""

import csv
import os


import numpy as np

from .converters import Converter
from .decode import _decode_fixed_length, _decode_variable_length
from .packet_fields import PacketField, PacketArray
from ccsdspy import log

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
        # List of PacketField instances
        self._fields = fields[:]

        # Dictionary mapping input name to tuple (output_name: str, Converter instance)
        self._converters = {}

    @classmethod
    def from_file(cls, file):
        """
        Parameters
        ----------
        file : str
           Path to file on the local file system that defines the packet fields.
           Currently only supports csv files.
           See :download:`basic_csv_3col.csv <../../ccsdspy/tests/data/packet_def/basic_csv_3col.csv>`  # noqa: E501
           and :download:`extended_csv_4col.csv <../../ccsdspy/tests/data/packet_def/extended_csv_4col.csv>`  # noqa: E501

        Returns
        -------
        An instance of FixedLength.

        Raises
        ------
        ValueError
            If the file type is not supported. Currently on CSV files are supported.
        """
        file_extension = os.path.splitext(file)
        if file_extension[1] == ".csv":
            fields = _get_fields_csv_file(file)
        else:
            raise ValueError(f"File type {file_extension[1]} not supported.")

        return cls(fields)

    def add_converted_field(self, input_field_name, output_field_name, converter):
        """Add a converted field to the packet definition, used to apply
        post-processing transformations of decoded fields.

        Parameters
        ----------
        input_field_name : str or list/tuple
           Name of input field, or list/tuple of names of fields. There must be field(s)
           which exists in the packet definition corresponding to these name(s).
        output_field_name : str
           Name of output field. When the packet is decoded using `pkt.load()`,
           a new field named this will be present in the output dictionary.
        converter : instance of subclass of `:py:class:~ccsdspy.converters.Converter`
           A converter object to apply post-processing conversions, such as
           calibration curves or value replacement. Converter objects
           can be found in`:py:mod:~ccsdspy.converters`.

        Raises
        ------
        TypeError
           If one of the arguments is not of the correct type.
        ValueError
           The provided `input_field_name` is not present in the packet definition
        """
        if not isinstance(output_field_name, str):
            raise TypeError("output_field_name must be a str")
        if not isinstance(converter, Converter):
            raise TypeError("converter must be an instance of a Converter subclass")

        # Get tuple of input field names for storing; this handles the input_field_name
        # argument being either a str, or list/tuple
        if isinstance(input_field_name, str):
            input_field_names = (input_field_name,)
        elif isinstance(input_field_name, (list, tuple)):
            input_field_names = tuple(input_field_name)
        else:
            raise TypeError("input_field_name must be either str, list, or tuple")

        del input_field_name  # don't use the variable again in this function

        # Check that each of the input field names exists in the packet, and report
        # the missing fields if not
        # Collect valid names of fields, which include primary header fields as well
        # as fields defined in the packet.
        fields_in_packet_set = set()

        for field in _prepend_primary_header_fields(self._fields):
            fields_in_packet_set.add(field._name)

        input_field_names_set = set(input_field_names)
        all_fields_present = input_field_names_set <= fields_in_packet_set  # subset

        if not all_fields_present:
            missing_fields = input_field_names_set - fields_in_packet_set  # set op A \ B
            raise ValueError(
                "Some fields specified as inputs to converters were missing: "
                f"{sorted(missing_fields)}"
            )

        self._converters[input_field_names] = (output_field_name, converter)


class FixedLength(_BasePacket):
    """Define a fixed length packet to decode binary data.

    Fixed length packets correspond to packets that are the same length and
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
        if any(isinstance(field._array_shape, str) for field in fields):
            raise ValueError(
                "The FixedLength class does not support variable fields. "
                "Instead, use the VariableLength class."
            )

        self._init(fields)

    def load(self, file, include_primary_header=False, reset_file_obj=False):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file : str
           Path to file on the local file system, or file-like object
        include_primary_header : bool
           If True, provides the primary header in the output. The names of the
           fields are: `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`,
           `CCSDS_SECONDARY_FLAG`, `CCSDS_SEQUENCE_FLAG`, `CCSDS_APID`,
           `CCSDS_SEQUENCE_COUNT`, and `CCSDS_PACKET_LENGTH`
        reset_file_obj : bool
           If True, leave the file object, when it is file buffer, where it was before load is called.
           Otherwise, (default), leave the file stream pos after the read packets.
           Does not apply when file is a string.

        Returns
        -------
        field_arrays : dict, string to NumPy array
            dictionary mapping field names to NumPy arrays, with key order matching
            the order of fields in the packet.

        Warns
        -----
        UserWarning
            If the ccsds sequence count is not in order
        UserWarning
            If the ccsds sequence count is missing packets
        UserWarning
            If there are more than one APID
        """
        packet_arrays = _load(
            file,
            self._fields,
            self._converters,
            "fixed_length",
            include_primary_header=True,
            reset_file_obj=reset_file_obj,
        )

        # inspect the primary header and issue warning if appropriate
        _inspect_primary_header_fields(packet_arrays)

        if not include_primary_header:
            _delete_primary_header_fields(packet_arrays)

        return packet_arrays


class VariableLength(_BasePacket):
    """Define a variable length packet to decode binary data.

    Variable length packets are packets which have a different length each
    time.  Variable length fields are defined as `~ccsdspy.PacketArray` fields
    where `array_shape="expand"` (causing the field to grow to fill the packet) or
    `array_shape="other_field"` (causes the field named `other_field` to set the number
    of elements in this array).

    Please note that while this class is able to parse fixed length packets, it
    is much slower. Use the :py:class:`~ccsdspy.FixedLength` class instead.

    Rules for variable length packets:
      * Do only specify a `~ccsdspy.PacketArray` with the `array_shape="other_field"`
        when `other_field` precedes it in the packet definition
      * Do not provide more than one expanding `~ccsdspy.PacketArray` with `array_shape="expand"`
      * Do not specify the primary header fields manually
      * Do not specify explicit bit_offsets (they will be computed automatically)
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
        # Check there is only one expanding field in the packet definition
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

        # Check variable fields with their sizes set by other fields only do so when
        # the previous field precedes it
        field_names = [field._name for field in fields]

        for i, field in enumerate(fields):
            if (
                isinstance(field, PacketArray)
                and isinstance(field._array_shape, str)
                and field._array_shape != "expand"
                and field._array_shape not in field_names[:i]
            ):
                raise ValueError(
                    "The VariableLength class requires that variable fields with "
                    "their sizes set by other fields only do so when the "
                    "previous field precedes it."
                )

        # Check that bit offsets are not set
        if not all(field._bit_offset is None for field in fields):
            raise ValueError(
                "The VariableLength class does not support explicit bit "
                "offsets. You must specify the entire packet so they can be "
                "determined automatically."
            )

        self._init(fields)

    def load(self, file, include_primary_header=False, reset_file_obj=False):
        """Decode a file-like object containing a sequence of these packets.

        Parameters
        ----------
        file : str
           Path to file on the local file system, or file-like object
        include_primary_header : bool
           If True, provides the primary header in the output. The names of the
           fields are: `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`,
           `CCSDS_SECONDARY_FLAG`, `CCSDS_SEQUENCE_FLAG`, `CCSDS_APID`,
           `CCSDS_SEQUENCE_COUNT`, and `CCSDS_PACKET_LENGTH`
        reset_file_obj : bool
           If True, leave the file object, when it is file buffer, where it was before load is called.
           Otherwise, (default), leave the file stream pos after the read packets.
           Does not apply when file is a string.

        Returns
        -------
        field_arrays : dict, string to NumPy array
            dictionary mapping field names to NumPy arrays, with key order matching
            the order of fields in the packet.

        Warns
        -----
        UserWarning
            If the ccsds sequence count is not in order
        UserWarning
            If the ccsds sequence count is missing packets
        UserWarning
            If there are more than one APID
        """
        # The variable length decoder requires the full packet definition, so if
        # they didn't want the primary header fields, we parse for them and then
        # remove them after.
        packet_arrays = _load(
            file,
            self._fields,
            self._converters,
            "variable_length",
            include_primary_header=True,
            reset_file_obj=reset_file_obj,
        )

        # inspect the primary header and issue warning if appropriate
        _inspect_primary_header_fields(packet_arrays)

        if not include_primary_header:
            _delete_primary_header_fields(packet_arrays)

        return packet_arrays


def _inspect_primary_header_fields(packet_arrays):
    """Inspects the primary header fields.

    Checks for the following issues
    * all apids are the same
    * sequence count is not missing any values
    * sequence count is in order

    Parameters
    -----------
    packet_arrays
        dictionary mapping field names to NumPy arrays, with key order matching
        the order fields in the packet. Modified in place

    Warns
    -----
    UserWarning
        If the ccsds sequence count is not in order
    UserWarning
        If the ccsds sequence count is missing packets
    UserWarning
        If there are more than one APID
    """
    seq_counts = packet_arrays["CCSDS_SEQUENCE_COUNT"]
    start, end = seq_counts[0], seq_counts[-1]
    missing_elements = sorted(set(range(start, end + 1)).difference(seq_counts))
    if len(missing_elements) != 0:
        log.warning(f"Missing packets found {missing_elements}.")

    if not np.all(seq_counts == np.sort(seq_counts)):
        log.warning("Sequence count are out of order.")

    individual_ap_ids = set(packet_arrays["CCSDS_APID"])
    if len(individual_ap_ids) != 1:
        log.warning(f"Found multiple AP IDs {individual_ap_ids}.")

    return None


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
        if existing_field._field_type != "array" or isinstance(existing_field._array_shape, str):
            return_fields.append(existing_field)
            continue

        array_shape = existing_field._array_shape
        array_order = existing_field._array_order

        index_vecs = [np.arange(dim) for dim in array_shape]
        index_grids = np.meshgrid(*index_vecs, indexing="ij")
        indices_flat = [index_grid.flatten(order=array_order) for index_grid in index_grids]

        expand_history[existing_field._name] = {
            "shape": array_shape,
            "data_type": existing_field._data_type,
            "fields": {},
        }

        for i, indices in enumerate(zip(*indices_flat)):
            name = f"{existing_field._name}[{','.join(map(str,indices))}]"
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

            expand_history[existing_field._name]["fields"][name] = indices
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

        for element_name, indices in array_details["fields"].items():
            array.__setitem__((slice(None),) + indices, field_arrays[element_name])
            # get index of the position where the array field was
            pos = list(return_field_arrays.keys()).index(element_name)
            del return_field_arrays[element_name]

        # do the following trick to insert the unexpanded array where the expanded arrays fields were.
        return_field_items = list(return_field_arrays.items())
        return_field_items.insert(pos, (array_name, array))
        return_field_arrays = dict(return_field_items)

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


def _parse_csv_array_shape(data_type_str):
    """Parse a data type string from a CSV to determine the array shape.

    Parameters
    ----------
    data_type_str : str
        Full string specifying the data type, e.g. `uint(1, 2)`

    Returns
    -------
    array_shape : str, int, tuple of int
       Parsed array shape to be used in loading CSV.

    Raises
    ------
    ValueError
        If the array shape is not valid. Must be `expand`, the name of another field,
        or a tuple of ints.
    """
    array_shape_str = data_type_str[data_type_str.find("(") + 1 : data_type_str.find(")")]
    if array_shape_str == "expand":
        array_shape = "expand"
    elif "," in array_shape_str:
        try:
            array_shape = tuple(map(int, array_shape_str.split(", ")))
        except ValueError:
            raise ValueError(
                "Array shape must be `expand`, the name of another field, or a tuple of ints."
            )
    else:  # string is either another field for reference or a single integer for a one dimensional array shape
        array_shape = int(array_shape_str) if array_shape_str.isnumeric() else array_shape_str
    return array_shape


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

    Raises
    ------
    RuntimeError
        If the CSV file is empty.
    ValueError
        If the CSV file does not contain the required columns. Must have at least `name`, `data_type`, and `bit_length`.
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
            if "bit_offset" not in headers:  # basic 3 col csv file
                if (row["data_type"].count("(") == 1) and (row["data_type"].count(")") == 1):
                    data_type = row["data_type"].split("(")[0]
                    array_shape = _parse_csv_array_shape(row["data_type"])
                    fields.append(
                        PacketArray(
                            name=row["name"],
                            data_type=data_type,
                            bit_length=int(row["bit_length"]),
                            array_shape=array_shape,
                        )
                    )
                else:
                    fields.append(
                        PacketField(
                            name=row["name"],
                            data_type=row["data_type"],
                            bit_length=int(row["bit_length"]),
                        )
                    )
            if "bit_offset" in headers:  # extended 4 col csv file provides bit offsets
                # TODO: Check the consistency of bit_offsets versus previous bit_lengths
                if (row["data_type"].count("(") == 1) and (row["data_type"].count(")") == 1):
                    data_type = row["data_type"].split("(")[0]
                    array_shape = _parse_csv_array_shape(row["data_type"])
                    fields.append(
                        PacketArray(
                            name=row["name"],
                            data_type=data_type,
                            bit_length=int(row["bit_length"]),
                            bit_offset=int(row["bit_offset"]),
                            array_shape=array_shape,
                        )
                    )
                else:
                    fields.append(
                        PacketField(
                            name=row["name"],
                            data_type=row["data_type"],
                            bit_length=int(row["bit_length"]),
                            bit_offset=int(row["bit_offset"]),
                        )
                    )

    return fields


def _load(
    file, fields, converters, decoder_name, include_primary_header=False, reset_file_obj=False
):
    """Decode a file-like object containing a sequence of these packets.

    Parameters
    ----------
    file: str
       Path to file on the local file system, or file-like object
    fields : list of `ccsdspy.PacketField`
       Layout of packet fields contained in the definition.
    converters : dict, str to tuple (str, Converter)
       Dictionary of post-processing conversions. keys are input field names,
       values are tuples of (output_field_name, Converter instance)
    decoder_name: {'fixed_length', 'variable_length'}
       String identifying which decoder to use.
    include_primary_header: bool
       If True, provides the primary header in the output
    reset_file_obj : bool
           If True, leave the file object, when it is a file buffer, where it was before _load is called.
           Otherwise, (default), leave the file stream pos after the read packets.
           Does not apply when file is a string.

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
        file_pos = file.tell()
        file_bytes = np.frombuffer(file.read(), "u1")
    else:
        file_bytes = np.fromfile(file, "u1")

    orig_fields = fields

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
    field_arrays = _apply_post_byte_reoderings(field_arrays, orig_fields)
    field_arrays = _apply_converters(field_arrays, converters)

    if hasattr(file, "read") and reset_file_obj:
        file.seek(file_pos)
    return field_arrays


def _apply_converters(field_arrays, converters):
    """Apply post-processing converters in place to a dictionary of field
    arrays.

    Parameters
    ----------
    field_arrays : dict of string to NumPy arrays
       The decoded packet field arrays without any post-processing applied
    converters : dict, str to tuple (str, Converter)
       Dictionary of post-processing conversions. keys are input field names,
       values are tuples of (output_field_name, Converter instance)

    Returns
    -------
    converted_field_arrays : dict of string to NumPy arrays
       The converted decoded packet field arrays, as a dictionary with the same
       key as the passed `field_arrays`.
    """
    converted = field_arrays.copy()

    for input_field_names, (output_field_name, converter) in converters.items():
        # Collect list of input arrays to pass as *args to converter function
        input_arrays = []

        for input_field_name in input_field_names:
            input_arrays.append(field_arrays[input_field_name])

        # Call converter function
        converted[output_field_name] = converter.convert(*input_arrays)

    return converted


def _apply_post_byte_reoderings(field_arrays, orig_fields):
    """Step of load procedure to apply post-processing byte reorderings.

    A field gets post-processing byte reordering if the attribute
      `field._byte_order_post` is not None.

    Parameters
    ----------
    field_arrays : dict of string to NumPy arrays
       The decoded packet field arrays without any post-processing applied
    orig_fields : List of PacketField
       Original fields as specified in the packet, before any replacements
       which occur in the processing step.

    Returns
    -------
    Reference to argument field_arrays (object was mutuated).
    """
    for field in orig_fields:
        if field._byte_order_post is None:
            continue

        byte_order_string = field._byte_order_post
        byte_order_ints = [int(digit) for digit in byte_order_string]
        is_obj_array = field_arrays[field._name].dtype == object

        if is_obj_array:
            new_packet_arrays = []

            for i, packet_array in enumerate(field_arrays[field._name]):
                field_arrays[field._name][i] = _do_array_byte_reordering(
                    packet_array, byte_order_ints
                )
        else:
            field_arrays[field._name] = _do_array_byte_reordering(
                field_arrays[field._name], byte_order_ints
            )

    return field_arrays


def _do_array_byte_reordering(array, byte_order_ints):
    """Reorder the bytes of an array.

    Parameters
    ----------
    array : NumPy array
      May be multidimensional. Dtype of array must not be object.
    byte_order_ints : list of int
      Inceces of the bytes in order, e.g., 2314.

    Returns
    -------
    Array with bytes reordered according to the passed order.
    """
    assert array.dtype != object, "Error in byte reordering, please report a bug:.{array.dtype}"

    parsed_byte_length = array.itemsize
    native_byte_length = max(byte_order_ints)

    array_bytes = array.copy()
    array_bytes.dtype = np.uint8
    array_bytes = array_bytes.reshape((array.size, parsed_byte_length))

    digits_zero_idx = [digit - 1 for digit in reversed(byte_order_ints)]
    select_indeces = []
    select_indeces.extend(digits_zero_idx)
    select_indeces.extend(sorted(set(range(array.itemsize)) - set(digits_zero_idx)))

    padding = array.itemsize - len(byte_order_ints)
    reordered = np.zeros_like(array_bytes)

    for i in range(reordered.shape[0]):
        reordered[i, :] = array_bytes[i, ::-1][select_indeces]

    shifted = np.zeros_like(reordered)

    if padding > 0:
        shifted[:, padding:] = reordered[:, :-padding]
    else:
        shifted[:] = reordered

    shifted.dtype = array.dtype
    shifted = shifted.reshape(array.shape)

    return shifted
