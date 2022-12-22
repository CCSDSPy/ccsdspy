"""Tests for the ccsdspy.interface module.
"""
__author__ = "Daniel da Silva"

import io
import os.path
import struct

import numpy as np
import pytest

from ..interface import FixedLength, PacketField, PacketArray, _get_fields_csv_file

dir_path = os.path.dirname(os.path.realpath(__file__))
packet_def_dir = os.path.join(dir_path, "data", "packet_def")
csv_file_4col = os.path.join(packet_def_dir, "simple_csv_4col.csv")
csv_file_3col = os.path.join(packet_def_dir, "simple_csv_3col.csv")


def test_PacketField_initializer_raises_ValueError_on_bad_data_type():
    """Asserts that the PacketField class raises a ValueError when an invalid
    data_type is provided.
    """
    with pytest.raises(ValueError):
        PacketField(name="mnemonic", data_type="fizz", bit_length=1)
    with pytest.raises(ValueError):
        PacketField(name="mnemonic", data_type="uint", bit_length=1, byte_order="bloop")


def test_PacketField_initializer_raises_TypeError_on_bad_types():
    """Asserts that the PacketField class raises a TypeError
    when arguments are of the wrong type.
    """
    with pytest.raises(TypeError):
        PacketField(name=1, data_type="uint", bit_length=1)
    with pytest.raises(TypeError):
        PacketField(name="mnemonic", data_type=1, bit_length=1)
    with pytest.raises(TypeError):
        PacketField(name="mnemonic", data_type="uint", bit_length="foobar")
    with pytest.raises(TypeError):
        PacketField(name="mnemonic", data_type="uint", bit_length=4, bit_offset="foo")


def test_PacketField_repr():
    field = PacketField(name="MyField", data_type="uint", bit_length=1)

    assert "PacketField" in repr(field)
    assert "MyField" in repr(field)


def test_PacketField_iter():
    field = PacketField(name="MyField", data_type="uint", bit_length=1)
    assert dict(field)["name"] == "MyField"
    assert dict(field)["dataType"] == "uint"


def test_FixedLength_initializer_copies_field_list():
    """Tests that the FixedLengthPacket initializer stores a copy of the
    provided fields list.
    """
    fields = [PacketField(name="mnemonic", data_type="uint", bit_length=8)]
    pkt = FixedLength(fields)
    assert pkt._fields is not fields


def test_get_fields_csv_file_3col():
    """Test that the csv reader parses the 3 column test file correctly."""

    names = []
    data_types = []
    bit_lengths = []
    with open(csv_file_3col, "r") as fp:
        lines = fp.readlines()
        num_lines = len(lines)
        for line in lines[1:]:  # skip the header row
            cols = line.split(",")
            names.append(cols[0].strip())
            data_types.append(cols[1].strip())
            bit_lengths.append(int(cols[2]))

    fields = _get_fields_csv_file(csv_file_3col)

    assert num_lines - 1 == len(fields)
    for i, this_field in enumerate(fields):
        assert this_field._name == names[i]
        assert this_field._data_type == data_types[i]
        assert this_field._bit_length == bit_lengths[i]


def test_get_fields_csv_file_4col():
    """Test that the csv reader parses the 4 column test file correctly."""

    names = []
    data_types = []
    bit_lengths = []
    bit_offsets = []
    with open(csv_file_4col, "r") as fp:
        lines = fp.readlines()
        num_lines = len(lines)
        for line in lines[1:]:  # skip the header row
            cols = line.split(",")
            names.append(cols[0].strip())
            data_types.append(cols[1].strip())
            bit_lengths.append(int(cols[2]))
            bit_offsets.append(int(cols[3]))

    fields = _get_fields_csv_file(csv_file_4col)

    assert num_lines - 1 == len(fields)
    for i, this_field in enumerate(fields):
        assert this_field._name == names[i]
        assert this_field._data_type == data_types[i]
        assert this_field._bit_length == bit_lengths[i]
        assert this_field._bit_offset == bit_offsets[i]


def test_FixedLength_from_file():
    """Test that from_file returns a FixedLength instance"""
    assert isinstance(FixedLength.from_file(csv_file_3col), FixedLength)
    assert isinstance(FixedLength.from_file(csv_file_4col), FixedLength)


@pytest.mark.parametrize("filename", ["boo.txt", "great.zip"])
def test_FixedLength_from_file_not_supported(filename):
    """Test that if given an unsupported filetype raises an error"""
    with pytest.raises(ValueError):
        FixedLength.from_file(filename)


@pytest.mark.parametrize(
    "numpy_dtype,ccsdspy_data_type,ccsdspy_bit_length,array_order",
    [
        (">f4", "float", 32, "C"),
        (">f4", "float", 32, "F"),
        (">u2", "uint", 16, "C"),
        (">u2", "uint", 16, "F"),
        (">u8", "uint", 64, "C"),
        (">u8", "uint", 64, "F"),
        (">i4", "int", 32, "C"),
        (">i4", "int", 32, "F"),
    ],
)
def test_multidimensional_array(
    numpy_dtype, ccsdspy_data_type, ccsdspy_bit_length, array_order
):
    """Test the PacketArray class with a multidimensional array.

    See test_hs.py for a test with a 1-dimensional array
    """
    # Each packet holds a 32x4 array where the array of the k'th packet has:
    #   arr[i, j] = k * (2 * i + j)
    num_packets = 10
    arrays = {}

    for k in range(num_packets):
        arrays[k] = np.zeros((32, 4), dtype=numpy_dtype)

        for i in range(32):
            for j in range(4):
                arrays[k][i, j] = k * (2 * i + j)

    # Generate packets
    apid = 0x08E2
    packet_id = int("0001100000000000", 2) + apid
    packet_stream = b""

    for packet_num in range(num_packets):
        packet_length = arrays[packet_num].nbytes - 1
        this_packet = struct.pack(">HHH", packet_id, packet_num, packet_length)
        this_packet += arrays[packet_num].tobytes(order=array_order)
        packet_stream += this_packet

    assert len(packet_stream) == num_packets * (6 + arrays[0].nbytes)

    # Build fixed length parse packet stream
    pkt = FixedLength(
        [
            PacketArray(
                name="array",
                data_type=ccsdspy_data_type,
                bit_length=ccsdspy_bit_length,
                array_shape=(32, 4),
                array_order=array_order,
            )
        ]
    )
    results = pkt.load(io.BytesIO(packet_stream))

    # Check results
    for k in range(num_packets):
        for i in range(32):
            for j in range(4):
                assert results["array"][k, i, j] == k * (2 * i + j)
