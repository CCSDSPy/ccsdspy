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
    with pytest.raises(TypeError):
        PacketField(name="mnemonic", data_type="uint", bit_length=4, description=12345)


def test_PacketField_repr():
    field = PacketField(name="MyField", data_type="uint", bit_length=1)

    assert "PacketField" in repr(field)
    assert "MyField" in repr(field)


def test_PacketField_iter():
    field = PacketField(name="MyField", data_type="uint", bit_length=1)
    assert dict(field)["name"] == "MyField"
    assert dict(field)["dataType"] == "uint"


def test_PacketField_raises_AttributeError_on_set_description():
    field = PacketField(name="MyField", data_type="uint", bit_length=1, description="A field")
    with pytest.raises(AttributeError):
        field.description = "New description"


def test_PacketArray_TypeErrors():
    with pytest.raises(TypeError):
        PacketArray(
            name="mnemonic",
            data_type="uint",
            array_shape=30,
            bit_length=1,
            array_order=3,  # must be str
        )

    with pytest.raises(TypeError):
        PacketArray(
            name="mnemonic",
            data_type="uint",
            array_shape=30,
            bit_length=1,
            array_order="X",  # invalid str
        )

    # Array shape must be either str or tuple
    with pytest.raises(TypeError):
        PacketArray(
            name="mnemonic",
            data_type="",
            array_shape={3, 4, 5},
            bit_length=1,
        )

    # Array shape must be >= 0 for all dims
    with pytest.raises(TypeError):
        PacketArray(
            name="mnemonic",
            data_type="",
            array_shape=(3, -2, 4),
            bit_length=1,
        )

    # Sum of array shape must be nonzero
    with pytest.raises(TypeError):
        PacketArray(
            name="mnemonic",
            data_type="",
            array_shape=(0, 0, 0),
            bit_length=1,
        )


def test_PacketArray_sets_default_data_type_expanding():
    # checks sets data type to uint when not specified (when expanding)
    field = PacketArray(name="mnemonic", bit_length=1, array_shape="expand")
    assert field._data_type == "uint"

    # checks rejects data type set thats not uint (when expanding)
    with pytest.raises(ValueError):
        PacketArray(name="mnemonic", bit_length=1, data_type="fill", array_shape="expand")
