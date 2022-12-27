"""Tests for VariableLength class and data in tests/data/var_length"""

import os

import numpy as np
import pytest

from .. import VariableLength, PacketField, PacketArray


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_var_length_data(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(dir_path, "data", "var_length", "var_length_packets.bin")

    pkt = VariableLength(
        [
            PacketArray(
                name="data",
                data_type="uint",
                bit_length=16,
                array_shape="expand",
            )
        ]
    )

    field_arrays = pkt.load(bin_path, include_primary_header=include_primary_header)

    assert field_arrays["data"].dtype == object
    assert field_arrays["data"].size == 10

    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for i in range(10):
        assert field_arrays["data"][i].shape == (sizes[i],)
        expected = np.arange(sizes[i], 2 * sizes[i])
        assert np.all(field_arrays["data"][i] == expected)


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_var_length_data_with_footer(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(
        dir_path, "data", "var_length", "var_length_packets_with_footer.bin"
    )

    pkt = VariableLength(
        [
            PacketArray(
                name="data",
                data_type="uint",
                bit_length=16,
                array_shape="expand",
            ),
            PacketField(name="footer", data_type="uint", bit_length=16),
        ]
    )

    field_arrays = pkt.load(bin_path, include_primary_header=include_primary_header)

    assert field_arrays["data"].dtype == object
    assert field_arrays["data"].size == 10
    assert np.all(field_arrays["footer"] == 1)

    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for i in range(10):
        assert field_arrays["data"][i].shape == (sizes[i],)
        expected = np.arange(sizes[i], 2 * sizes[i])
        assert np.all(field_arrays["data"][i] == expected)
