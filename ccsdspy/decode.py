"""Internal decoding routines."""
from __future__ import division
from collections import namedtuple
from pickle import bytes_types

import numpy as np

from ccsdspy.constants import (
    BITS_PER_BYTE,
    PRIMARY_HEADER_NUM_BYTES,
)

__author__ = "Daniel da Silva <mail@danieldasilva.org>"


def _get_packet_total_bytes(primary_header_bytes):
    """Parse the number of bytes in a packet from the bytes associated
    with a packet's primary header.

    Parameters
    ----------
    primary_header_bytes : bytes
      Bytes associated with the packet primary header, of length
      `ccsdspy.constants.PRIMARY_HEADER_NUM_BYTES`.

    Returns
    -------
    num_bytes : int
      Total number of bytes in the packet, including the primary header.

    Raises
    ------
    ValueError
       The number of bytes in the supplied argument is too short. It must be
       of length `ccsdspy.constants.PRIMARY_HEADER_NUM_BYTES`.
    """
    if len(primary_header_bytes) != PRIMARY_HEADER_NUM_BYTES:
        raise ValueError(
            f"Primary header byte sequence must be {PRIMARY_HEADER_NUM_BYTES} bytes long"
        )

    # These variables are named based on 1-indexing
    primary_header_byte5 = primary_header_bytes[4]
    primary_header_byte6 = primary_header_bytes[5]

    # Number of bytes listed in the orimary header. The value in the
    # primary header is the number of byes in the body minus one.
    num_bytes = primary_header_byte5 << BITS_PER_BYTE
    num_bytes += primary_header_byte6
    num_bytes += 1
    num_bytes += PRIMARY_HEADER_NUM_BYTES

    return num_bytes


def _get_packet_apid(primary_header_bytes):
    """Parse the APID of a packet from the bytes associated
    with a packet's primary header.

    Parameters
    ----------
    primary_header_bytes : bytes
      Bytes associated with the packet primary header, of length
      `ccsdspy.constants.PRIMARY_HEADER_NUM_BYTES`.

    Raises
    ------
    ValueError
       The number of bytes in the supplied argument is too short. It must be
       of length `ccsdspy.constants.PRIMARY_HEADER_NUM_BYTES`.
    """
    if len(primary_header_bytes) != PRIMARY_HEADER_NUM_BYTES:
        raise ValueError(
            f"Primary header byte sequence must be {PRIMARY_HEADER_NUM_BYTES} bytes long"
        )

    # These variables are named based on 1-indexing
    primary_header_byte1 = primary_header_bytes[0]
    primary_header_byte2 = primary_header_bytes[1]

    # Read as 2-byte unisgned integer and mask out unwanted parts of the first
    # byte
    apid = primary_header_byte1 << BITS_PER_BYTE
    apid += primary_header_byte2
    apid &= 0x07FF

    return apid


def _decode_fixed_length(file_bytes, fields):
    """Decode a fixed length packet stream of a single APID.

    Parameters
    ----------
    file_bytes : array
       A NumPy array of uint8 type, holding the bytes of the file to decode.
    fields : list of ccsdspy.PacketField
       A list of fields, including the secondary header but excluding the
       primary header.

    Returns
    -------
    dictionary mapping field names to NumPy arrays, stored in the same order as
    the fields array passed.
    """
    # Setup a dictionary mapping a bit offset to each field. It is assumed
    # that the `fields` array contains entries for the secondary header.
    packet_nbytes = _get_packet_total_bytes(file_bytes[:PRIMARY_HEADER_NUM_BYTES])
    body_nbytes = sum(field._bit_length for field in fields) // BITS_PER_BYTE
    counter = (packet_nbytes - body_nbytes) * BITS_PER_BYTE

    bit_offset = {}

    for i, field in enumerate(fields):
        if i == 0 and field._bit_offset is not None:
            # case: using bit_offset to fix the start position
            bit_offset[field._name] = field._bit_offset
            counter = field._bit_offset + field._bit_length
        elif field._bit_offset is None:
            # case: floating start position such that packet def fills to
            # to end of packet. What's missing is assumed to be header at the beginning.
            bit_offset[field._name] = counter
            counter += field._bit_length
        elif field._bit_offset < counter:
            # case: bit_offset specifying to backtrack. This condition
            # seems odd and unlikely. Eg. one or more bits of a packet overlap?
            bit_offset[field._name] = field._bit_offset
            # don't update counter unless the the overlap goes past counter
            counter = max(field._bit_offset + field._bit_length, counter)
        elif field._bit_offset >= counter:
            # case: otherwise, bit_offset is ahead of counter and we're skipping
            # definition of 0 or more bits.
            bit_offset[field._name] = field._bit_offset
            counter = field._bit_offset + field._bit_length
        else:
            raise RuntimeError(
                f"Unexpected case: could not compare"
                f" bit_offset {field._bit_offset} with "
                f"counter {counter} for field {field._name}"
            )

    if all(field._bit_offset is None for field in fields):
        assert counter == packet_nbytes * BITS_PER_BYTE, "Field definition != packet length"
    elif counter > packet_nbytes * BITS_PER_BYTE:
        raise RuntimeError(
            (
                "Packet definition larger than packet length"
                f" by {counter-(packet_nbytes*BITS_PER_BYTE)} bits"
            )
        )

    # Setup metadata for each field, consiting of where to look for the field in
    # the file and how to parse it.
    FieldMeta = namedtuple("Meta", ["nbytes_file", "start_byte_file", "nbytes_final", "np_dtype"])
    field_meta = {}

    for field in fields:
        nbytes_file = np.ceil(field._bit_length / BITS_PER_BYTE).astype(int)

        if (
            bit_offset[field._name] % BITS_PER_BYTE
            and bit_offset[field._name] % BITS_PER_BYTE + field._bit_length > BITS_PER_BYTE
        ):
            nbytes_file += 1

        nbytes_final = {3: 4, 5: 8, 6: 8, 7: 8}.get(nbytes_file, nbytes_file)
        start_byte_file = bit_offset[field._name] // BITS_PER_BYTE

        # byte_order_symbol is only used to control float types here.
        #  - uint and int byte order are handled with byteswap later
        #  - fill is independent of byte order (all 1's)
        #  - byte order is not applicable to str types
        byte_order_symbol = "<" if field._byte_order == "little" else ">"
        np_dtype = {
            "uint": ">u%d" % nbytes_final,
            "int": ">i%d" % nbytes_final,
            "fill": "S%d" % nbytes_final,
            "float": "%sf%d" % (byte_order_symbol, nbytes_final),
            "str": "S%d" % nbytes_final,
        }[field._data_type]

        field_meta[field] = FieldMeta(nbytes_file, start_byte_file, nbytes_final, np_dtype)

    # Read the file and calculate length of packet and number of packets in the
    # file. Trim extra bytes that may have occurred by a break in the downlink
    # while a packet was beign transferred.
    extra_bytes = file_bytes.size % packet_nbytes

    if extra_bytes > 0:
        file_bytes = file_bytes[:-extra_bytes]

    packet_count = file_bytes.size // packet_nbytes

    # Create byte arrays for each field. At the end of this method they are left
    # as the numpy uint8 type.
    field_bytes = {}

    for field in fields:
        meta = field_meta[field]
        arr = np.zeros(packet_count * meta.nbytes_final, "u1")
        xbytes = meta.nbytes_final - meta.nbytes_file

        for i in range(xbytes, meta.nbytes_final):
            arr[i :: meta.nbytes_final] = file_bytes[
                meta.start_byte_file + i - xbytes :: packet_nbytes
            ]
            field_bytes[field] = arr

    # Switch dtype of byte arrays to the final dtype, and apply masks and shifts
    # to interpret the correct bits.
    field_arrays = {}

    for field in fields:
        meta = field_meta[field]
        arr = field_bytes[field]
        arr.dtype = meta.np_dtype

        if field._data_type in ("int", "uint"):
            xbytes = meta.nbytes_final - meta.nbytes_file

            bitmask_left = (
                bit_offset[field._name]
                + BITS_PER_BYTE * xbytes
                - BITS_PER_BYTE * meta.start_byte_file
            )

            bitmask_right = BITS_PER_BYTE * meta.nbytes_final - bitmask_left - field._bit_length

            bitmask_left, bitmask_right = np.array([bitmask_left, bitmask_right]).astype(
                meta.np_dtype
            )

            bitmask = np.zeros(arr.shape, meta.np_dtype)
            bitmask |= (1 << int(BITS_PER_BYTE * meta.nbytes_final - bitmask_left)) - 1
            tmp = np.left_shift([1], bitmask_right)
            bitmask &= np.bitwise_not(tmp[0] - 1).astype(meta.np_dtype)

            arr &= bitmask
            arr >>= bitmask_right

            if field._byte_order == "little":
                arr.byteswap(inplace=True)

        field_arrays[field._name] = arr

    return field_arrays


def _decode_variable_length(file_bytes, fields):
    """Decode a variable length packet stream of a single APID.

    Parameters
    ----------
    file_bytes : array
       A NumPy array of uint8 type, holding the bytes of the file to decode.
    fields : list of ccsdspy.PacketField
       A list of fields, excluding the
       primary header.

    Returns
    -------
    dict
    A dictionary mapping field names to NumPy arrays, stored in the same order as the fields.
    """
    # Get start indeces of each packet -------------------------------------
    packet_starts = []
    offset = 0

    while offset < len(file_bytes):
        packet_starts.append(offset)
        offset += file_bytes[offset + 4] * 256 + file_bytes[offset + 5] + 7

    assert offset == len(file_bytes)
    npackets = len(packet_starts)

    # Setup a dictionary mapping a bit offset to each field. It is assumed
    # that the `fields` array contains entries for the secondary header.
    # Negative bit offsets are referenced from the end of the packet.
    # ------------------------------------------------------------------------
    bit_offsets = {}
    counter = 0
    expand_idx = None

    for i, field in enumerate(fields):
        if field._bit_offset is None:
            if field._array_shape == "expand" and counter % BITS_PER_BYTE != 0:
                raise RuntimeError(
                    "Expanding fields must be byte aligned. Found an instance "
                    f"where not in field named '{field._name}'"
                )

            bit_offsets[field._name] = counter
            counter += field._bit_length

            if field._array_shape == "expand":
                expand_idx = i
                break
        else:
            bit_offsets[field._name] = field._bit_offset
            counter = max(field._bit_offset + field._bit_length, counter)

    if expand_idx is not None:
        counter = 0
        footer_fields = fields[expand_idx + 1 :]
        for i, field in enumerate(reversed(footer_fields)):
            bit_offsets[field._name] = counter - field._bit_length
            counter -= field._bit_length

    # Initialize output dicitonary of field arrays. Expanding fields will be
    # an array of dtype=object (jagged array), which will be an array refrence
    # at each index. Non-expanding fields are the matched to the most suitable
    # data type.
    # ------------------------------------------------------------------------
    field_arrays = {}  # return value of this function
    numpy_dtypes = {}

    for field in fields:
        # Number of bytes that the field spans in the file
        bit_offset = bit_offsets[field._name]
        nbytes_file = (
            (bit_offset + field._bit_length - 1) // BITS_PER_BYTE - bit_offset // BITS_PER_BYTE + 1
        )

        # NumPy only has 2-byte, 4-byte and 8-byte variants (eg, float16, float32,
        # float64, but not float48). Map them to an nbytes for the output.
        nbytes_final = {3: 4, 5: 8, 6: 8, 7: 8}.get(nbytes_file, nbytes_file)

        # byte_order_symbol is only used to control float types here.
        #  - uint and int byte order are handled with byteswap later
        #  - fill is independent of byte order (all 1's)
        #  - byte order is not applicable to str types
        byte_order_symbol = "<" if field._byte_order == "little" else ">"
        np_dtype = {
            "uint": ">u%d" % nbytes_final,
            "int": ">i%d" % nbytes_final,
            "fill": "S%d" % nbytes_final,
            "float": "%sf%d" % (byte_order_symbol, nbytes_final),
            "str": "S%d" % nbytes_final,
        }[field._data_type]

        numpy_dtypes[field._name] = np_dtype

        if field._array_shape == "expand":
            field_arrays[field._name] = np.zeros(npackets, dtype=object)
        else:
            field_arrays[field._name] = np.zeros(npackets, dtype=np_dtype)

    # Loop through packets
    # ----------------------------------------------------------------------------
    for pkt_num, packet_start in enumerate(packet_starts):
        packet_nbytes = file_bytes[packet_start + 4] * 256 + file_bytes[packet_start + 5] + 7

        for i, field in enumerate(fields):
            field_raw_data = None  # will be array of uint8
            if bit_offsets[field._name] < 0:
                # Footer byte after expanding field: Referenced from end of packet
                start_byte = (
                    packet_start + packet_nbytes + bit_offsets[field._name] // BITS_PER_BYTE
                )
            else:
                # Header byte before expanding field: Referenced from start of packet
                start_byte = packet_start + bit_offsets[field._name] // BITS_PER_BYTE

            if field._array_shape == "expand":
                footer_bits = sum(field._bit_length for field in fields[i + 1 :])
                assert footer_bits % BITS_PER_BYTE == 0, "Expanding field must be byte aligned"
                stop_byte = packet_start + packet_nbytes - footer_bits // BITS_PER_BYTE
                field_raw_data = file_bytes[start_byte:stop_byte]
            else:
                # Get field_raw_data, which are the bytes of the field as uint8 for this
                # packet
                bit_offset = bit_offsets[field._name]
                nbytes_file = (
                    (bit_offset + field._bit_length - 1) // BITS_PER_BYTE
                    - bit_offset // BITS_PER_BYTE
                    + 1
                )

                nbytes_final = {3: 4, 5: 8, 6: 8, 7: 8}.get(nbytes_file, nbytes_file)
                xbytes = nbytes_final - nbytes_file
                field_raw_data = np.zeros(nbytes_final, "u1")
                # inds = []

                for i in range(xbytes, nbytes_final):
                    idx = start_byte + i - xbytes
                    field_raw_data[i] = file_bytes[idx]

            # Switch dtype of byte arrays to the final dtype, and apply masks and shifts
            # to interpret the correct bits.
            field_raw_data.dtype = numpy_dtypes[field._name]

            if field._data_type in ("int", "uint"):
                last_byte = start_byte + nbytes_file
                end_last_parent_byte = last_byte * BITS_PER_BYTE

                b = bit_offsets[field._name]
                if b < 0:
                    b = packet_nbytes * BITS_PER_BYTE + bit_offsets[field._name]

                last_occupied_bit = packet_start * BITS_PER_BYTE + b + field._bit_length
                left_bits_before_shift = b % BITS_PER_BYTE
                right_shift = end_last_parent_byte - last_occupied_bit

                assert right_shift >= 0

                if left_bits_before_shift > 0:
                    mask = int("1" * ((nbytes_file * BITS_PER_BYTE) - left_bits_before_shift), 2)
                    field_raw_data &= mask

                if right_shift > 0 and field._array_shape != "expand":
                    field_raw_data >>= right_shift

                if field._byte_order == "little":
                    field_raw_data.byteswap(inplace=True)

            # Set the field in the final array
            if field._array_shape == "expand":
                field_arrays[field._name][pkt_num] = field_raw_data
            else:
                field_arrays[field._name][pkt_num] = field_raw_data[0]

    return field_arrays
