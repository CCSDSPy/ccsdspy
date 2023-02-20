"""Tests for the ccsdspy.packet_types module"""

__author__ = "Daniel da Silva"

import io
import os.path
import struct

import numpy as np
import pytest

from .. import FixedLength, VariableLength, PacketField, PacketArray
from ..packet_types import _get_fields_csv_file

dir_path = os.path.dirname(os.path.realpath(__file__))
packet_def_dir = os.path.join(dir_path, "data", "packet_def")
csv_file_4col = os.path.join(packet_def_dir, "simple_csv_4col.csv")
csv_file_3col = os.path.join(packet_def_dir, "simple_csv_3col.csv")
csv_file_4col_with_array = os.path.join(packet_def_dir, "simple_csv_4col_with_array.csv")
csv_file_3col_with_array = os.path.join(packet_def_dir, "simple_csv_3col_with_array.csv")


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
    assert isinstance(FixedLength.from_file(csv_file_3col_with_array), FixedLength)
    assert isinstance(FixedLength.from_file(csv_file_4col_with_array), FixedLength)


@pytest.mark.parametrize("filename", ["boo.txt", "great.zip"])
def test_FixedLength_from_file_not_supported(filename):
    """Test that if given an unsupported filetype raises an error"""
    with pytest.raises(ValueError):
        FixedLength.from_file(filename)


@pytest.mark.parametrize(
    "cls,numpy_dtype,ccsdspy_data_type,ccsdspy_bit_length,array_order,include_bit_offset",
    [
        (FixedLength, ">f4", "float", 32, "C", False),
        (FixedLength, ">f4", "float", 32, "F", False),
        (FixedLength, ">u2", "uint", 16, "C", False),
        (FixedLength, ">u2", "uint", 16, "F", False),
        (FixedLength, ">u8", "uint", 64, "C", False),
        (FixedLength, ">u8", "uint", 64, "F", False),
        (FixedLength, ">i4", "int", 32, "C", False),
        (FixedLength, ">i4", "int", 32, "F", False),
        (FixedLength, ">i4", "int", 32, "F", True),
        (VariableLength, ">f4", "float", 32, "C", False),
        (VariableLength, ">f4", "float", 32, "F", False),
        (VariableLength, ">u2", "uint", 16, "C", False),
        (VariableLength, ">u2", "uint", 16, "F", False),
        (VariableLength, ">u8", "uint", 64, "C", False),
        (VariableLength, ">u8", "uint", 64, "F", False),
        (VariableLength, ">i4", "int", 32, "C", False),
        (VariableLength, ">i4", "int", 32, "F", False),
    ],
)
def test_multidimensional_array(
    cls,
    numpy_dtype,
    ccsdspy_data_type,
    ccsdspy_bit_length,
    array_order,
    include_bit_offset,
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
    if include_bit_offset:
        bit_offset = 48
    else:
        bit_offset = None

    pkt = cls(
        [
            PacketArray(
                name="array",
                data_type=ccsdspy_data_type,
                bit_length=ccsdspy_bit_length,
                array_shape=(32, 4),
                array_order=array_order,
                bit_offset=bit_offset,
            )
        ]
    )
    results = pkt.load(io.BytesIO(packet_stream))

    # Check results
    for k in range(num_packets):
        for i in range(32):
            for j in range(4):
                assert results["array"][k, i, j] == k * (2 * i + j)


def test_fixed_length_save():
    """Save a fixed length packet and then parse it and make sure that the input is the same as the output."""
    pkt = FixedLength(
        [
            PacketField(name="DATAU", data_type="uint", bit_length=32),
            PacketField(name="DATAI", data_type="int", bit_length=16),
            PacketField(name="DATAF", data_type="float", bit_length=64),
            PacketField(name="DATAS", data_type="str", bit_length=8),
            PacketArray(
                name="SENSOR_GRID",
                data_type="uint",
                bit_length=16,
                array_shape=(32, 32),
                array_order="C",
            ),
        ]
    )
    num_packets = 1000
    pkt_type = 1
    apid = 0x084
    sec_header_flag = 1
    seq_flag = 0
    datau = np.arange(0, num_packets, dtype=np.uint32)
    datai = np.arange(1, num_packets + 1, dtype=np.int16)
    dataf = np.arange(2, num_packets + 2, dtype=np.float64)
    # shift to make first element 'a'
    datas = np.arange(97, num_packets + 97, dtype=np.uint8)
    sensor_grid = np.arange(0, num_packets * 32 * 32, dtype=np.uint16).reshape(num_packets, 32, 32)

    data = {
        "DATAU": datau,
        "DATAI": datai,
        "DATAF": dataf,
        "DATAS": datas,
        "SENSOR_GRID": sensor_grid,
    }

    pkt.save("test.bin", pkt_type, apid, sec_header_flag, seq_flag, data)
    result = pkt.load("test.bin", include_primary_header=True)

    assert len(result["DATAU"]) == len(datau)
    assert len(result["DATAI"]) == len(datai)
    assert len(result["DATAF"]) == len(dataf)
    assert len(result["DATAS"]) == len(datas)
    assert len(result["SENSOR_GRID"]) == len(sensor_grid)
    assert result["SENSOR_GRID"].shape == sensor_grid.shape

    assert np.all(result["CCSDS_PACKET_TYPE"] == pkt_type)
    assert np.all(result["CCSDS_SECONDARY_FLAG"] == sec_header_flag)
    assert np.all(result["CCSDS_APID"] == apid)
    assert np.all(result["CCSDS_SEQUENCE_FLAG"] == seq_flag)

    assert np.allclose(result["DATAU"], datau)
    assert np.allclose(result["DATAI"], datai)
    assert np.allclose(result["DATAF"], dataf)
    assert np.allclose(result["DATAS"].view("uint8"), datas)
    assert np.allclose(result["SENSOR_GRID"], sensor_grid)


def test_variable_length_save():
    """Save a variable length packet and then parse it and make sure that the input is the same as the output."""

    pkt = VariableLength(
        [
            PacketField(name="DATAU", data_type="uint", bit_length=32),
            PacketField(name="DATAI", data_type="int", bit_length=16),
            PacketField(name="DATAF", data_type="float", bit_length=64),
            PacketField(name="DATAS", data_type="str", bit_length=8),
            PacketArray(
                name="DATAEXPAND",
                data_type="uint",
                bit_length=8,
                array_shape="expand",
            ),
        ]
    )
    num_packets = 1000
    pkt_type = 1
    apid = 0x084
    sec_header_flag = 1
    seq_flag = 0
    datau = np.arange(0, num_packets, dtype=np.uint32)
    datai = np.arange(1, num_packets + 1, dtype=np.int16)
    dataf = np.arange(2, num_packets + 2, dtype=np.float64)
    # shift to make first element 'a'
    datas = np.arange(97, num_packets + 97, dtype=np.uint8)
    data_expand_length = np.random.randint(1, 10, size=num_packets)
    data_expand = []
    for i in range(num_packets):
        data_expand.append(np.random.randint(1, 10, size=data_expand_length[i], dtype=np.uint8))

    data = {
        "DATAU": datau,
        "DATAI": datai,
        "DATAF": dataf,
        "DATAS": datas,
        "DATAEXPAND": data_expand,
    }

    pkt.save("test.bin", pkt_type, apid, sec_header_flag, seq_flag, data)
    result = pkt.load("test.bin", include_primary_header=True)

    assert len(result["DATAU"]) == len(datau)
    assert len(result["DATAI"]) == len(datai)
    assert len(result["DATAF"]) == len(dataf)
    assert len(result["DATAS"]) == len(datas)
    assert len(result["DATAEXPAND"]) == len(data_expand)

    assert np.all(result["CCSDS_PACKET_TYPE"] == pkt_type)
    assert np.all(result["CCSDS_SECONDARY_FLAG"] == sec_header_flag)
    assert np.all(result["CCSDS_APID"] == apid)
    assert np.all(result["CCSDS_SEQUENCE_FLAG"] == seq_flag)

    assert np.allclose(result["DATAU"], datau)
    assert np.allclose(result["DATAI"], datai)
    assert np.allclose(result["DATAF"], dataf)
    assert np.allclose(result["DATAS"].view("uint8"), datas)
    for i in range(len(result["DATAEXPAND"])):
        assert np.allclose(result["DATAEXPAND"][i], data_expand[i])
