"""Tests for VariableLength class and data in tests/data/var_length"""

import os

import numpy as np

from .. import VariableLength, PacketField, PacketArray


def test_var_length_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(
        dir_path, "data", "var_length", "var_length_packets.bin"
    )
    
    pkt = VariableLength([
        PacketArray(
            name='data',
            data_type='uint',
            bit_length=16,
            array_shape='expand',
        )
    ])

    field_arrays = pkt.load(bin_path)

    assert field_arrays['data'].dtype == object

    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23,  29]
    
    for i in range(10):
        assert field_arrays['data'][i].shape == (sizes[i],)
        expected = np.arange(sizes[i], 2*sizes[i])
        assert np.all(field_arrays['data'][i] == expected)

