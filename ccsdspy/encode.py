"""Internal encoding routines.

The functionality in this module is written using the bitstruct module to
pack individual bits. CCSDSPy packet definitions are converted to bitstruct
format strings, and the function bistruct.pack() is used.
"""

import bitstruct
import numpy as np

from .constants import BITS_PER_BYTE


def _undo_array_byte_reordering(array, byte_order_ints):
    """Apply inverse byte reordering to prepare data for encoding.

    This function reverses the transformation done by packet_types._do_array_byte_reordering()
    so that data can be encoded with the correct byte order.

    The decode process does:
    1. Reverses input bytes: reversed_bytes = bytes[::-1]
    2. Selects: reordered = reversed_bytes[select_indices]
    3. Applies padding shift

    To invert for encoding:
    1. Undo padding shift
    2. Invert selection: reversed_bytes[select_indices[j]] = reordered[j]
    3. Reverse again: bytes = reversed_bytes[::-1]

    Parameters
    ----------
    array : NumPy array
        User data values. May be multidimensional. Dtype must not be object.
    byte_order_ints : list of int
        Byte order specification, e.g., [4, 3, 2, 1] for "4321".

    Returns
    -------
    Array with values transformed so that when bitstruct packs them (as big-endian),
    the decode process will recover the original values.
    """
    assert array.dtype != object, f"Error in byte reordering: {array.dtype}"

    # Get byte representation of user values (as big-endian)
    array_copy = array.copy()
    array_copy.dtype = np.uint8
    array_copy = array_copy.reshape((array.size, array.itemsize))

    # Compute decode parameters
    digits_zero_idx = [digit - 1 for digit in reversed(byte_order_ints)]
    select_indeces = []
    select_indeces.extend(digits_zero_idx)
    select_indeces.extend(sorted(set(range(array.itemsize)) - set(digits_zero_idx)))
    padding = array.itemsize - len(byte_order_ints)

    result = np.zeros_like(array_copy)

    for i in range(array_copy.shape[0]):
        # Current bytes represent the user's value
        user_bytes = array_copy[i, :]

        # Step 1: Undo the padding shift from decode
        # Decode did: shifted[:, padding:] = reordered[:, :-padding]
        # So: reordered[:, :-padding] = shifted[:, padding:]
        if padding > 0:
            reordered_bytes = np.zeros(array.itemsize, dtype=np.uint8)
            reordered_bytes[:-padding] = user_bytes[padding:]
        else:
            reordered_bytes = user_bytes.copy()

        # Step 2: Invert the selection
        # Decode did: reordered[j] = reversed_input[select_indeces[j]]
        # So: reversed_input[select_indeces[j]] = reordered[j]
        reversed_bytes = np.zeros(array.itemsize, dtype=np.uint8)
        for j in range(len(select_indeces)):
            reversed_bytes[select_indeces[j]] = reordered_bytes[j]

        # Step 3: Reverse to get original (file) bytes
        file_bytes = reversed_bytes[::-1]

        result[i, :] = file_bytes

    # Convert back to original dtype
    result.dtype = array.dtype
    result = result.reshape(array.shape)

    return result


def _prepare_field_for_encoding(field, data, packet_num):
    """Prepare field data for encoding by applying byte order transformations.

    This function applies the necessary byte order transformations to field data
    before it's packed using bitstruct.pack(). Since bitstruct always packs in
    big-endian, we need to convert from little-endian or custom byte orders.

    Parameters
    ----------
    field : PacketField
        The field definition containing byte order information.
    data : array-like
        The data for this field (for a single packet if element, or array if PacketArray).
    packet_num : int
        The packet number (index) in the field_arrays.

    Returns
    -------
    Transformed data ready for bitstruct.pack().
    """
    # For str and fill types, no byte order transformation needed
    if field._data_type in ('str', 'fill'):
        return data

    # Float types are handled by bitstruct format string, no pre-processing needed
    if field._data_type == 'float':
        return data

    # Handle int and uint types with byte order
    if field._data_type in ('int', 'uint'):
        # Convert to numpy array for consistent handling
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        else:
            data = data.copy()  # Don't modify original

        # Ensure at least 1D for consistent handling
        original_shape = data.shape
        if data.ndim == 0:
            data = data.reshape(1)

        # First handle custom byte orders if present
        if field._byte_order_post is not None:
            byte_order_ints = [int(digit) for digit in field._byte_order_post]
            data = _undo_array_byte_reordering(data, byte_order_ints)

        # Then handle little endian: reverse bytes so bitstruct packs them correctly
        # This happens AFTER custom byte order because _byte_order_parse is set to "big"
        # when custom byte order is used
        elif field._byte_order_parse == 'little':
            # The user wants little-endian bytes in the file.
            # bitstruct.pack() always outputs big-endian bytes.
            # So we need to reverse the byte order of our values before passing to bitstruct.
            # Example: user has 0x12345678 (as int), wants file bytes [78 56 34 12] (little endian)
            # We pass 0x78563412 to bitstruct, it writes [78 56 34 12] treating it as big endian

            # Calculate byte size from bit_length
            byte_size = (field._bit_length + 7) // 8

            # Convert to object array to hold Python ints
            flat_data = data.flatten()
            result_list = []

            for val in flat_data:
                # Convert value to bytes using field's bit_length, reverse them, convert back
                # Always treat as unsigned during byte reversal to avoid sign issues
                # bitstruct will handle the sign interpretation based on format string
                is_signed = field._data_type == 'int'
                val_bytes = int(val).to_bytes(byte_size, byteorder='big', signed=is_signed)
                reversed_bytes = val_bytes[::-1]
                # Interpret reversed bytes as signed if original was signed
                result_list.append(int.from_bytes(reversed_bytes, byteorder='big', signed=is_signed))

            # Return as list or reshaped array
            if data.shape == ():
                data = result_list[0]
            elif data.ndim == 1:
                data = np.array(result_list)
            else:
                data = np.array(result_list).reshape(data.shape)

        # Restore original shape
        data = data.reshape(original_shape)

        return data

    return data


# Dictionary which maps CCSDSPy data types to a corresponding data type used
# by the bitstruct module.
DATA_TYPE_CCSDSPY_TO_BITSTRUCT = {"str": "u", "int": "s", "uint": "u", "float": "f", "fill": "uint"}

# The CCSDSPy header specified in terms of a bitstruct format string
PRIMARY_HEADER_FMT_BITSTRUCT = "u3u1u1u11u2u14u16"


def _encode_fixed_length(
    fields, expand_fields, field_arrays, pkt_type, apid, sec_header_flag, seq_flag
):
    """Encode a sequence of fields and accompanying field arrays into a binary
    stream of packets. This is the variant for fixed length packets.
    """
    _raise_if_field_arrays_not_same_length(field_arrays)

    # Apply byte order transformations to field_arrays before encoding.
    # bitstruct.pack() expects big-endian data, so we convert from little-endian
    # or custom byte orders to big-endian.
    field_arrays_encoded = {}
    for field in fields:
        field_data = field_arrays[field._name]
        if field._field_type == "element":
            # For scalar fields, process each packet value
            encoded_values = []
            for packet_num in range(len(field_data)):
                encoded_val = _prepare_field_for_encoding(field, field_data[packet_num], packet_num)
                encoded_values.append(encoded_val)
            field_arrays_encoded[field._name] = np.array(encoded_values)
        elif field._field_type == "array":
            # For array fields, process each packet's array
            encoded_arrays = []
            for packet_num in range(len(field_data)):
                encoded_arr = _prepare_field_for_encoding(field, field_data[packet_num], packet_num)
                encoded_arrays.append(encoded_arr)
            field_arrays_encoded[field._name] = np.array(encoded_arrays, dtype=object) if any(
                isinstance(x, np.ndarray) for x in encoded_arrays
            ) else np.array(encoded_arrays)

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
    num_packets = len(next(iter(field_arrays_encoded.values())))

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
                val = field_arrays_encoded[field._name][packet_num]
                # Convert numpy types to Python native types for bitstruct
                if isinstance(val, np.ndarray) and val.ndim == 0:
                    val = val.item()
                elif isinstance(val, (np.integer, np.floating)):
                    val = val.item()
                pack_values.append(val)
            elif field._field_type == "array":
                pack_values.extend(field_arrays_encoded[field._name][packet_num].flatten().tolist())

        # Add to packet stream using bitstruct.pack()
        packet_stream += bitstruct.pack(pack_format, *pack_values)

    return packet_stream


def _encode_variable_length(
    fields, expand_fields, field_arrays, pkt_type, apid, sec_header_flag, seq_flag
):
    """Encode a sequence of fields and accompanying field arrays into a binary
    stream of packets. This is the variant for variable length packets.
    """
    _raise_if_field_arrays_not_same_length(field_arrays)

    # The bitstruct.pack() function is used to pack the individual bits. This
    # function takes a pack format string which specifies something analogous
    # to a low-level packet definition, and a list of values which correspond
    # to that.
    packet_stream = b""
    num_packets = len(next(iter(field_arrays.values())))  # use any array

    for packet_num in range(num_packets):
        # Apply byte order transformations for this packet.
        # bitstruct.pack() expects big-endian data, so we convert from little-endian
        # or custom byte orders to big-endian.
        packet_field_values = {}
        for field in fields:
            field_data = field_arrays[field._name][packet_num]
            encoded_data = _prepare_field_for_encoding(field, field_data, packet_num)
            packet_field_values[field._name] = encoded_data

        # Generate pack format. This starts from the primary header format (a
        # constant), and then is appended for each field in the packet definition.
        # The expanded fields are used for convenience.
        pack_format = PRIMARY_HEADER_FMT_BITSTRUCT

        for field in expand_fields:
            if field._field_type == "array" and field._array_shape == "expand":
                field_num_items = len(packet_field_values[field._name])
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
                pack_values.append(packet_field_values[field._name])
            elif field._field_type == "array" and field._array_shape != "expand":
                pack_values += list(packet_field_values[field._name].flatten())
            elif field._field_type == "array" and field._array_shape == "expand":
                pack_values += list(packet_field_values[field._name])

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
