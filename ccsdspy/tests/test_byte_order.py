"""Tests for complex byte orderings, eg. 3412.

The test data covers all XTCE orderings requested in 
https://github.com/CCSDSPy/ccsdspy/discussions/110
"""

import glob
import itertools
import os
import string

import numpy as np
import pytest

from ccsdspy import (
    PacketField,
    PacketArray,
    VariableLength,
    FixedLength,
)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

PARAM_BYTE_ORDER_FILES = glob.glob(f"{CUR_DIR}/data/byte_order/byteorder*.bin")
PARAM_CLASSES = [FixedLength, VariableLength]
PARAM_USEARRAYS = [False, True]
PARAM_OPTIONS = list(itertools.product(
    PARAM_BYTE_ORDER_FILES,
    PARAM_CLASSES,
    PARAM_USEARRAYS
))


@pytest.mark.parametrize("bin_file,cls,use_arrays", PARAM_OPTIONS)
def test_byte_order(bin_file, cls, use_arrays):
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

    if use_arrays:        
        # Build Packet with PacketArray instance
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
    else:
        # Build Packet with individual fields
        packet_fields = []
        
        for i in range(80):
            packet_fields.append(
                PacketField(
                    name=f'body{i}',
                    data_type='uint',
                    bit_length=8*len(byte_order),
                    byte_order=byte_order
                )
            )
        packet = cls(packet_fields)
        result = packet.load(bin_file)
        
        for pkt_num, expected_data in enumerate(expected_file_data):
            got_data = [result[f'body{i}'][pkt_num] for i in range(80)]            
            np.testing.assert_array_equal(got_data, expected_data)
        
