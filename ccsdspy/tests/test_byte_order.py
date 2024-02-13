"""Tests for complex byte orderings, eg. 3412.

The test data covers all XTCE orderings requested in 
  https://github.com/CCSDSPy/ccsdspy/discussions/110

See also:
  ccsdspy/tests/data/byte_order/byte_order_packets.py
"""
import glob
import itertools
import os
import string

import numpy as np
import pytest

from ccsdspy import (
    PacketField,
    PacketArray,
    VariableLength,
    FixedLength,
)

# Current directory of the module we are in.
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# The test_byte_order function takes combinational variations of arguments.
# These constants and the itertools.product() function create these
# combinations.
PARAM_BYTE_ORDER_FILES = glob.glob(f"{CUR_DIR}/data/byte_order/byteorder*.bin")
PARAM_CLASSES = [FixedLength, VariableLength]
PARAM_DECODEMETHODS = ["array", "fields", "multiarray"]
PARAM_OPTIONS = list(itertools.product(PARAM_BYTE_ORDER_FILES, PARAM_CLASSES, PARAM_DECODEMETHODS))


@pytest.mark.parametrize("bin_file,cls,decode_method", PARAM_OPTIONS)
def test_byte_order(bin_file, cls, decode_method):
    """Test loading a .bin file and matching its contents to its .csv
    counterpart.

    See also:
      ccsdspy/tests/data/byte_order/byte_order_packets.py
    """
    csv_file = bin_file.replace(".bin", ".csv")
    assert os.path.exists(bin_file)
    assert os.path.exists(csv_file)

    byte_order = os.path.basename(bin_file).split(".")[0].split("_")[1]
    assert all((char in string.digits) for char in byte_order)

    # Parse CSV file
    expected_file_data = []

    with open(csv_file) as fh:
        for line in fh:
            line_values = [int(v) for v in line.strip().split(",")]
            expected_file_data.append(line_values)

    expected_file_data = np.array(expected_file_data)

    if decode_method in ("array", "multiarray", "expand"):
        shape = {
            "array": 80,
            "multiarray": (40, 2),
            "expand": "expand",
        }[decode_method]

        # Build Packet with PacketArray instance
        packet = cls(
            [
                PacketArray(
                    name="body",
                    data_type="uint",
                    array_shape=shape,
                    bit_length=8 * len(byte_order),
                    byte_order=byte_order,
                )
            ]
        )
        result = packet.load(bin_file)

        for got_data, expected_data in zip(result["body"], expected_file_data):
            if decode_method == "multiarray":
                expected_data = np.array(expected_data).reshape(shape)

            np.testing.assert_array_equal(got_data, expected_data)
    else:
        # Build Packet with individual fields
        packet_fields = []

        for i in range(80):
            packet_fields.append(
                PacketField(
                    name=f"body{i}",
                    data_type="uint",
                    bit_length=8 * len(byte_order),
                    byte_order=byte_order,
                )
            )
        packet = cls(packet_fields)
        result = packet.load(bin_file)

        for pkt_num, expected_data in enumerate(expected_file_data):
            got_data = [result[f"body{i}"][pkt_num] for i in range(80)]
            np.testing.assert_array_equal(got_data, expected_data)


def test_expanding():
    """Simple test for expanding fields."""
    bin_file = f"{CUR_DIR}/data/byte_order/byteorder_1234.bin"
    test_byte_order(bin_file, VariableLength, "expand")
