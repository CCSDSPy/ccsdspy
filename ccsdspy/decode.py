"""Internal decoding routines."""
from __future__ import division
from collections import namedtuple
import numpy as np

__author__ = 'Daniel da Silva <Daniel.e.daSilva@nasa.gov>'


def _decode_fixed_length(file_bytes, fields):
    """Decode a fixed length APID."""
    # Setup a dictionary mapping a bit offset to each field. It is assumed
    # that the `fields` array contains entries for the secondary header.
    packet_nbytes = file_bytes[4] * 256 + file_bytes[5] + 7
    body_nbytes = sum(field._bit_length for field in fields) // 8
    counter = (packet_nbytes - body_nbytes) * 8

    bit_offset = {}

    for field in fields:
        bit_offset[field._name] = counter
        counter += field._bit_length
        
    assert counter == packet_nbytes * 8, \
        'Missing {n} bits in packet definition!'.format(n=counter-packet_nbytes*8)
    
    # Setup metadata for each field, consiting of where to look for the field in
    # the file and how to parse it.
    FieldMeta = namedtuple('Meta', ['nbytes_file', 'start_byte_file',
                                    'nbytes_final', 'np_dtype'])
    field_meta = {}

    for field in fields:
        nbytes_file = np.ceil(field._bit_length/8.).astype(int)

        if bit_offset[field._name] % 8:
            nbytes_file += 1

        nbytes_final = {3: 4, 5: 8, 6: 8, 7: 8}.get(nbytes_file,  nbytes_file)
        start_byte_file = bit_offset[field._name] // 8

        np_dtype = {
            'uint': '>u%d' % nbytes_final,
            'int':  '>i%d' % nbytes_final,
            'fill': '>u%d' % nbytes_final,
        }[field._data_type]
        
        field_meta[field] = FieldMeta(
            nbytes_file, start_byte_file, nbytes_final, np_dtype)

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
        arr = np.zeros(packet_count * meta.nbytes_final, 'u1')
        xbytes = meta.nbytes_final - meta.nbytes_file

        for i in range(xbytes, meta.nbytes_final):
            arr[i::meta.nbytes_final] = (
                file_bytes[meta.start_byte_file + i - xbytes::packet_nbytes]
            )

        field_bytes[field] = arr

    # Switch dtype of byte arrays to the final dtype, and apply masks and shifts
    # to interpret the correct bits.
    field_arrays = {}

    for field in fields:
        meta = field_meta[field]
        arr = field_bytes[field]
        arr.dtype = meta.np_dtype
        xbytes = meta.nbytes_final - meta.nbytes_file

        bitmask_left = (bit_offset[field._name]
                        + 8 * xbytes
                        - 8 * meta.start_byte_file)

        bitmask_right = (8 * meta.nbytes_final
                         - bitmask_left
                         - field._bit_length)
     
        bitmask_left, bitmask_right = (
            np.array([bitmask_left, bitmask_right]).astype(meta.np_dtype)
        )

        bitmask = np.zeros(arr.shape, meta.np_dtype)
        bitmask |= (1 << int(8 * meta.nbytes_final - bitmask_left)) - 1
        tmp = np.left_shift([1], bitmask_right)
        bitmask &= np.bitwise_not(tmp[0] - 1).astype(meta.np_dtype)

        arr &= bitmask
        arr >>= bitmask_right

        field_arrays[field._name] = arr

    return field_arrays