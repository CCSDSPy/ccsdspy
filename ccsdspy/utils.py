"""Utils for the CCSDSPy package."""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"

from io import BytesIO
import warnings

import numpy as np

from . import VariableLength, PacketArray
from .constants import BITS_PER_BYTE, PRIMARY_HEADER_NUM_BYTES
from . import decode


def get_packet_total_bytes(primary_header_bytes):
    """[autogenerated]"""
    # Wrap around internal function from decode module
    return decode._get_packet_total_bytes(primary_header_bytes)


def get_packet_apid(primary_header_bytes):
    """[autogenerated]"""
    # Wrap around internal function from decode module
    return decode._get_packet_apid(primary_header_bytes)


# Copy __doc__ from decode module for functions which wrap decode module functions
# so that the doc need not be repeated in two places.
get_packet_total_bytes.__doc__ = decode._get_packet_total_bytes.__doc__
get_packet_apid.__doc__ = decode._get_packet_apid.__doc__


def iter_packet_bytes(file, include_primary_header=True):
    """Iterate through packets as raw bytes objects, in the order they appear in a file.

    This function works with mixed files containing multiple APIDs, which may
    include both fixed length and variable length packets.

    If end of last packet doesn't align with end of file, a warning is issued.

    Parameters
    ----------
    file : str, file-like
      Path to file on the local file system, or file-like object
    include_primary_header : bool
      If set to False, excludes the primary header bytes (the first six)

    Yields
    ------
    packet_bytes : bytes
       Bytes associated with each packet as it appears in the file. When
       include_primary_header=False, the primary header bytes are excluded.
    """
    if hasattr(file, "read"):
        file_bytes = np.frombuffer(file.read(), "u1")
    else:
        file_bytes = np.fromfile(file, "u1")

    offset = 0

    if include_primary_header:
        delta_idx = 0
    else:
        delta_idx = PRIMARY_HEADER_NUM_BYTES

    while offset < len(file_bytes):
        packet_nbytes = get_packet_total_bytes(
            file_bytes[offset : offset + PRIMARY_HEADER_NUM_BYTES].tobytes()
        )
        packet_bytes = file_bytes[offset + delta_idx : offset + packet_nbytes].tobytes()

        yield packet_bytes

        offset += packet_nbytes

    if offset != len(file_bytes):
        missing_bytes = offset - len(file_bytes)
        message = (
            f"File appears truncated-- missing {missing_bytes} byte (or " "maybe garbage at end)"
        )
        warnings.warn(message)


def split_packet_bytes(file, include_primary_header=True):
    """Retreive a list of bytes objects corresponding to each packet in a file.

    This function works with mixed files containing multiple APIDs, which may
    include both fixed length and variable length packets.

    If end of last packet doesn't align with end of file, a warning is issued.

    Parameters
    ----------
    file : str, file-like
      Path to file on the local file system, or file-like object
    include_primary_header : bool
      If set to False, excludes the primary header bytes (the first six)

    Returns
    -------
    packet_bytes : list of bytes
       List of bytes objects associated with each packet as it appears in the
       file. When include_primary_header=False, each byte object will have its
       primary header bytes excluded.
    """
    return list(iter_packet_bytes(file, include_primary_header=include_primary_header))


def read_primary_headers(file):
    """Read primary header fields and return contents as a dictionary
    of arrays.

    This function works with mixed files containing multiple APIDs, which may
    include both fixed length and variable length packets.

    Parameters
    ----------
    file : str, file-like
      Path to file on the local file system, or file-like object

    Returns
    -------
    header_arrays : dict, string to NumPy array
       Dictionary mapping header names to NumPy arrays. The header names are:
       `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`, `CCSDS_SECONDARY_FLAG`,
       `CCSDS_SEQUENCE_FLAG`, `CCSDS_APID`, `CCSDS_SEQUENCE_COUNT`,
       `CCSDS_PACKET_LENGTH`
    """
    pkt = VariableLength(
        [
            PacketArray(
                name="unused", data_type="uint", bit_length=BITS_PER_BYTE, array_shape="expand"
            )
        ]
    )

    header_arrays = pkt.load(file, include_primary_header=True)
    del header_arrays["unused"]

    return header_arrays


def split_by_apid(mixed_file, valid_apids=None):
    """Split a stream of mixed APIDs into separate streams by APID.

    This works with a mix of both fixed length and variable length packets.

    Parameters
    ----------
    mixed_file: str, file-like
       Path to file on the local file system, or file-like object
    valid_apids: list of int, None
       Optional list of valid APIDs. If specified, warning will be issued when
       an APID is encountered outside this list.

    Returns
    -------
    stream_by_apid : dict, int to :py:class:`~io.BytesIO`
      Dictionary mapping integer apid number to BytesIO instance with the file
      pointer at the beginning of the stream.
    """
    # If not None, convert valid_apids to set for faster lookup times
    if valid_apids is not None:
        valid_apids = set(valid_apids)

    stream_by_apid = {}

    for packet_bytes in iter_packet_bytes(mixed_file):
        apid = get_packet_apid(packet_bytes[:PRIMARY_HEADER_NUM_BYTES])

        if valid_apids is not None and apid not in valid_apids:
            warnings.warn(f"Found unknown APID {apid}")

        if apid not in stream_by_apid:
            stream_by_apid[apid] = BytesIO()

        stream_by_apid[apid].write(packet_bytes)

    for stream in stream_by_apid.values():
        stream.seek(0)

    return stream_by_apid


def count_packets(file, return_missing_bytes=False, return_extra_bytes=False):
    """Count the number of packets in a file and check if there are any
    missing bytes in the last packet.

    This function works with mixed files containing multiple APIDs, which may
    include both fixed length and variable length packets. When used with
    multiple APIDs, it simply returns the total number of packets of any APID.

    If end of last packet doesn't align with end of file, a warning is issued.

    Parameters
    ----------
    file : str, file-like
      Path to file on the local file system, or file-like object
    return_missing_bytes : bool, optional
      Also return the number of *missing* bytes at the end of the file. This
      is the number of bytes which would need to be added to the file to
      complete the last packet expected (as set by the packet length in
      the last packet's primary header).
    return_extra_bytes : bool, optional
      Also return the number of *extra* bytes at the end of the file. This
      is the number of bytes that exist after the last complete packet (as
      set by the packet length in the last complete packet's primary header).

    Returns
    -------
    num_packets : int
       Number of complete packets in the file
    missing_bytes : int or None, optional
      The number of bytes which would need to be added to the file to
      complete the last packet expected (as set by the packet length in
      the last packet's primary header).
    extra_bytes : int, optional
      The number of bytes at exist after the last complete packet (as set by
      the packet lacket in the last complete packet's primary header).

    """
    if hasattr(file, "read"):
        file_bytes = np.frombuffer(file.read(), "u1")
    else:
        file_bytes = np.fromfile(file, "u1")

    start_next_packet = 0
    num_packets = 0

    while True:
        next_primary_header = file_bytes[
            start_next_packet : start_next_packet + PRIMARY_HEADER_NUM_BYTES
        ].tobytes()
        next_primary_header_available = len(next_primary_header) == PRIMARY_HEADER_NUM_BYTES

        # If not enough for even another primary header
        if not next_primary_header_available:
            extra_bytes = len(file_bytes) - start_next_packet
            missing_bytes = None
            break

        # Read next primary header
        packet_nbytes = get_packet_total_bytes(next_primary_header)
        packet_complete = start_next_packet + packet_nbytes <= len(file_bytes)

        if not packet_complete:
            extra_bytes = len(file_bytes) - start_next_packet
            missing_bytes = start_next_packet + packet_nbytes - len(file_bytes) + 1
            break

        num_packets += 1
        start_next_packet += packet_nbytes

    if extra_bytes > 0:
        message = f"File appears truncated-- {extra_bytes} bytes at end"
        warnings.warn(message)

    # Return value depends on whether return_missing_bytes and return_extra_bytes
    # are set
    return_val = [num_packets]

    if return_missing_bytes:
        return_val.append(missing_bytes)
    if return_extra_bytes:
        return_val.append(extra_bytes)

    if len(return_val) == 1:
        return return_val[0]
    else:
        return tuple(return_val)
