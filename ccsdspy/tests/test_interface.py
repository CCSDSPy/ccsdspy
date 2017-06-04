"""Tests for the ccsdspy.interface module.
"""
__author__ = 'Daniel da Silva'

import pytest
from ..interface import PacketField, FixedLength


def test_PacketField_initializer_raises_ValueError_on_bad_data_type():
    """Asserts that the PacketField class raises a ValueError when an invalid
    data_type is provided.
    """
    with pytest.raises(ValueError):
        PacketField(name='mnemonic', data_type='fizz', bit_length=1)
    with pytest.raises(ValueError):
        PacketField(name='mnemonic', data_type='uint', bit_length=1,
                    byte_order='bloop')

        
def test_PacketField_initializer_raises_TypeError_on_bad_types():
    """Asserts that the PacketField class raises a TypeError
    when arguments are of the wrong type.
    """
    with pytest.raises(TypeError):
        PacketField(name=1, data_type='uint', bit_length=1)
    with pytest.raises(TypeError):
        PacketField(name='mnemonic', data_type=1, bit_length=1)
    with pytest.raises(TypeError):
        PacketField(name='mnemonic', data_type='uint', bit_length='foobar')
    with pytest.raises(TypeError):
        PacketField(name='mnemonic', data_type='uint', bit_length=4,
                    bit_offset='foo')


def test_PacketField_repr():
    field = PacketField(name='MyField', data_type='uint', bit_length=1)

    assert 'PacketField' in repr(field)
    assert 'MyField' in repr(field)

    
def test_FixedLength_initializer_copies_field_list():
    """Tests that the FixedLengthPacket initializer stores a copy of the 
    provided fields list.
    """
    fields = [PacketField(name='mnemonic', data_type='uint', bit_length=8)]
    pkt = FixedLength(fields)
    assert pkt._fields is not fields
        
