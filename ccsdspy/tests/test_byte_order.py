"""Tests for complex byte orderings, eg. 3412."""

import glob
import os
import string

import numpy as np
import pytest

from ccsdspy import PacketArray, VariableLength, FixedLength


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
BYTE_ORDER_FILES = glob.glob(f"{CUR_DIR}/data/byte_order/byteorder*.bin")


@pytest.mark.parametrize("bin_file", BYTE_ORDER_FILES)
def test_varlength(bin_file):
    _do_test(bin_file, VariableLength)


@pytest.mark.parametrize("bin_file", BYTE_ORDER_FILES)
def test_fixedlength(bin_file):
    _do_test(bin_file, FixedLength)

    
def _do_test(bin_file, cls):
    csv_file = bin_file.replace('.bin', '.csv')
    assert os.path.exists(bin_file)
    assert os.path.exists(csv_file)

    byte_order = os.path.basename(bin_file).split('.')[0].split('_')[1]
    assert all((char in string.digits) for char in byte_order)
    
    # Parse CSV file
    expected_file_data = []

    with open(csv_file) as fh:
        for line in fh:
            line_values = [int(v) for v in line.strip().split(',')]
            expected_file_data.append(line_values)

    expected_file_data = np.array(expected_file_data)
    
    # Build Packet
    packet = cls([
        PacketArray(
            name='body',
            data_type='uint',
            array_shape=80,
            bit_length=8*len(byte_order),
            byte_order=byte_order
        )
    ])
    result = packet.load(bin_file)
    
    for got_data, expected_data in zip(result['body'], expected_file_data):
        np.testing.assert_array_equal(got_data, expected_data)
    
