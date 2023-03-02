"""Internal encoding routines.

The functionality in this module is written using the bitstruct module to
pack individual bits. CCSDSPy packet definitions are converted to bitstruct
format strings, and the function bistruct.pack() is used. 
"""

import bitstruct
import numpy as np


# Dictionary which maps CCSDSPy data types to a corresponding data type used
# by the bitstruct module.
DATA_TYPE_CCSDSPY_TO_BITSTRUCT = {"str": "u", "int": "s", "uint": "u", "float": "f", "fill": "uint"}

# The CCSDSPy header specified in terms of a bitstruct format string
PRIMARY_HEADER_FMT_BITSTRUCT = "u3u1u1u11u2u14u16"

# Number of bits in a byte
BITS_PER_BYTE = 8


def _encode_fixed_length(
    fields, expand_fields, field_arrays, pkt_type, apid, sec_header_flag, seq_flag
):
    """Encode a sequence of fields and accompanying field arrays into a binary
    stream of packets. This is the variant for fixed length packets.
    """
    _raise_if_field_arrays_not_same_length(field_arrays)

    # The bitstruct.pack() function is used to pack the individual bits. This
    # function takes a pack format string which specifies something analogous
    # to a low-level packet definition, and a list of values which correspond
    # to that.
    # ------------------------------------------------------------------------
    # Generate the pack format for the entire packet before looping
    pack_format = PRIMARY_HEADER_FMT_BITSTRUCT

    for field in expand_fields:
        data_type_code = DATA_TYPE_CCSDSPY_TO_BITSTRUCT[field._data_type]
        pack_format += data_type_code + str(field._bit_length)

    packet_body_length_bits = bitstruct.calcsize(pack_format)
    packet_body_length_bits -= bitstruct.calcsize(PRIMARY_HEADER_FMT_BITSTRUCT)
    primary_header_packet_length = int(packet_body_length_bits / BITS_PER_BYTE - 1)

    # Loop through packets and pack values for use with bitstruct.pack(). These
    # start with the primary header values list, and then values for each field
    # are added.
    packet_stream = b""
    num_packets = len(next(iter(field_arrays.values())))

    for packet_num in range(num_packets):
        # Get list of pack values
        pack_values = [
            0,
            pkt_type,
            sec_header_flag,
            apid,
            seq_flag,
            packet_num,
            primary_header_packet_length,
        ]

        for field in fields:
            if field._field_type == "element":
                pack_values.append(field_arrays[field._name][packet_num])
            elif field._field_type == "array":
                pack_values.extend(field_arrays[field._name][packet_num].flatten().tolist())

        # Add to packet stream using bitstruct.pack()
        packet_stream += bitstruct.pack(pack_format, *pack_values)

    return packet_stream


def _encode_variable_length(
    fields, expand_fields, field_arrays, pkt_type, apid, sec_header_flag, seq_flag
):
    """Encode a sequence of fields and accompanying field arrays into a binary
    stream of packets. This is the variant for fixed length packets.
    """
    _raise_if_field_arrays_not_same_length(field_arrays)

    # The bitstruct.pack() function is used to pack the individual bits. This
    # function takes a pack format string which specifies something analogous
    # to a low-level packet definition, and a list of values which correspond
    # to that.
    packet_stream = b""
    num_packets = len(next(iter(field_arrays.values())))  # use any array

    for packet_num in range(num_packets):
        # Generate pack format. This starts from the primary header format (a
        # constant), and then is appended for each field in the packet definition.
        # The expanded fields are used for convinience.
        pack_format = PRIMARY_HEADER_FMT_BITSTRUCT

        for field in expand_fields:
            if field._field_type == "array" and field._array_shape == "expand":
                field_num_items = len(field_arrays[field._name][packet_num])
            else:
                field_num_items = 1

            item_format = DATA_TYPE_CCSDSPY_TO_BITSTRUCT[field._data_type] + str(field._bit_length)
            pack_format += item_format * field_num_items

        # Generate list of the values which correspond to the pack format string
        packet_body_length_bits = bitstruct.calcsize(pack_format)
        packet_body_length_bits -= bitstruct.calcsize(PRIMARY_HEADER_FMT_BITSTRUCT)
        primary_header_packet_length = int(packet_body_length_bits / BITS_PER_BYTE - 1)

        pack_values = [
            0,
            pkt_type,
            sec_header_flag,
            apid,
            seq_flag,
            packet_num,
            primary_header_packet_length,
        ]

        for field in fields:
            if field._field_type == "element":
                pack_values.append(field_arrays[field._name][packet_num])
            elif field._field_type == "array" and field._array_shape != "expand":
                pack_values += list(field_arrays[field._name][packet_num].flatten())
            elif field._field_type == "array" and field._array_shape == "expand":
                pack_values += list(field_arrays[field._name][packet_num])

        # Add to packet stream using bitstruct.pack()
        packet_stream += bitstruct.pack(pack_format, *pack_values)

    return packet_stream


def _raise_if_field_arrays_not_same_length(field_arrays):
    """Check all field arrays have the same length in the first dimension.

    Parameters
    ----------
    field_arrays : dict, string to NumPy array
      Dictionary mapping field names to NumPy arrays

    Raises
    ------
    ValueError
      The check fails and at the lengths are not all the same
    """
    field_array_lengths = [len(field_array) for field_array in field_arrays.values()]

    if np.unique(field_array_lengths).size > 1:
        raise ValueError(
            "Unable to write file when not all field arrays have the same "
            "length in the first dimension."
        )
