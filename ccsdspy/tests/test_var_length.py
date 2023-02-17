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
    assert all([arr.itemsize == 2 for arr in field_arrays["data"]])

    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for i in range(len(sizes)):
        try:
            assert field_arrays["data"][i].shape == (sizes[i],)
        except:
            import pdb

            pdb.set_trace()

        expected = np.arange(sizes[i], dtype="uint16") + sizes[i]
        assert np.all(field_arrays["data"][i] == expected)


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_var_length_data_with_footer(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(dir_path, "data", "var_length", "var_length_packets_with_footer.bin")

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
        expected = np.arange(sizes[i], dtype="uint16") + sizes[i]
        assert np.all(field_arrays["data"][i] == expected)


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_var_length_double_varfield_with_footer(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(
        dir_path, "data", "var_length", "var_length_packets_double_varfield_with_footer.bin"
    )

    pkt = VariableLength(
        [
            PacketField(name="data1_len", data_type="uint", bit_length=8),
            PacketArray(
                name="data1",
                data_type="uint",
                bit_length=16,
                array_shape="data1_len",
            ),
            PacketField(name="data2_len", data_type="uint", bit_length=8),
            PacketArray(
                name="data2",
                data_type="uint",
                bit_length=16,
                array_shape="data2_len",
            ),
            PacketField(name="footer", data_type="uint", bit_length=16),
        ]
    )

    field_arrays = pkt.load(bin_path, include_primary_header=include_primary_header)

    # Check footer
    assert np.all(field_arrays["footer"] == 1)

    # Check data1 array
    assert field_arrays["data1"].dtype == object
    assert field_arrays["data1"].size == 10
    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for i in range(10):
        assert field_arrays["data1"][i].shape == (sizes[i],)
        expected = np.arange(sizes[i], dtype="uint16") + sizes[i]
        assert np.all(field_arrays["data1"][i] == expected)

    # Check data2 array
    assert field_arrays["data2"].dtype == object
    assert field_arrays["data2"].size == 10
    sizes = [5, 7, 2, 8, 3, 41, 42, 1, 3, 4]

    for i in range(10):
        assert field_arrays["data2"][i].shape == (sizes[i],)
        expected = np.arange(sizes[i], dtype="uint16")
        assert np.all(field_arrays["data2"][i] == expected)
