"""Tests for the ccsdspy.interface module.
"""
__author__ = "Daniel da Silva"

import os.path

import pytest

from ..interface import FixedLength, PacketField, _get_fields_csv_file

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
