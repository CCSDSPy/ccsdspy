"""Tests for the ccsdspy.packet_fields module"""

import pytest

from .. import PacketField, PacketArray


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
