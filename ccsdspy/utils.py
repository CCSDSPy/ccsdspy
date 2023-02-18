"""Utils for the CCSDSPy package."""

__author__ = "Daniel da Silva <mail@danieldasilva.org>"

from io import BytesIO
import warnings

import numpy as np

from . import VariableLength, PacketArray


def read_primary_headers(file):
    """Read primary header fields and return contents as a dictionary
    of arrays.

    Parameters
    ----------
    file : str
      Path to file on the local file system, or file-like object

    Returns
    -------
    header_arrays : dict, string to NumPy array
       Dictionary mapping header names to NumPy arrays,The header names are:
       `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`, `CCSDS_SECONDARY_FLAG`,
       `CCSDS_SEQUENCE_FLAG`, `CCSDS_APID`, `CCSDS_SEQUENCE_COUNT`,
       `CCSDS_PACKET_LENGTH`
    """
    pkt = VariableLength(
        [PacketArray(name="unused", data_type="uint", bit_length=8, array_shape="expand")]
    )

    header_arrays = pkt.load(file, include_primary_header=True)
    del header_arrays["unused"]

    return header_arrays


def split_by_apid(mixed_file, valid_apids=None):
    """Split a stream of mixed APIDs into separate streams by APID.

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
    if hasattr(mixed_file, "read"):
        file_bytes = np.frombuffer(mixed_file.read(), "u1")
    else:
        file_bytes = np.fromfile(mixed_file, "u1")

    offset = 0
    stream_by_apid = {}

    while offset < len(file_bytes):
        packet_nbytes = file_bytes[offset + 4] * 256 + file_bytes[offset + 5] + 7

        apid = np.array([file_bytes[offset], file_bytes[offset + 1]], dtype=np.uint8)
        apid.dtype = ">u2"
        apid = apid[0]
        apid &= 0x07FF

        if valid_apids is not None and apid not in valid_apids:
            warnings.warn(f"Found unknown APID {apid}")

        if apid not in stream_by_apid:
            stream_by_apid[apid] = BytesIO()

        stream_by_apid[apid].write(file_bytes[offset : offset + packet_nbytes])
        offset += packet_nbytes

    if offset != len(file_bytes):
        missing_bytes = offset - len(file_bytes)
        message = (
            f"File appears truncated-- missing {missing_bytes} byte (or " "maybe garbage at end)"
        )
        warnings.warn(message)

    for stream in stream_by_apid.values():
        stream.seek(0)

    return stream_by_apid
