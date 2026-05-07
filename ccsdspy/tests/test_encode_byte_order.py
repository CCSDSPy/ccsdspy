"""Tests for byte order support in encoding.

These tests verify that packets can be encoded with various byte orders
(big, little, custom) and then decoded back correctly.
"""

import os
import tempfile

import numpy as np
import pytest

from ccsdspy import FixedLength, VariableLength, PacketField, PacketArray


class TestEncodeByteOrderFixedLength:
    """Test byte order encoding with FixedLength packets."""

    def test_encode_big_endian_uint(self):
        """Test encoding with big endian (default) uint field."""
        # Create packet with big endian field
        packet = FixedLength([
            PacketField(name='value', data_type='uint', bit_length=32, byte_order='big')
        ])

        # Create test data
        data = {'value': np.array([0x12345678, 0xAABBCCDD])}

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['value'], data['value'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_little_endian_uint(self):
        """Test encoding with little endian uint field."""
        # Create packet with little endian field
        packet = FixedLength([
            PacketField(name='value', data_type='uint', bit_length=32, byte_order='little')
        ])

        # Create test data
        data = {'value': np.array([0x12345678, 0xAABBCCDD])}

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['value'], data['value'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_little_endian_int(self):
        """Test encoding with little endian signed int field."""
        # Create packet with little endian field
        packet = FixedLength([
            PacketField(name='value', data_type='int', bit_length=32, byte_order='little')
        ])

        # Create test data with negative values
        data = {'value': np.array([-12345, 67890, -1])}

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['value'], data['value'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_custom_byte_order_4321(self):
        """Test encoding with custom byte order 4321."""
        # Create packet with custom byte order
        packet = FixedLength([
            PacketField(name='value', data_type='uint', bit_length=32, byte_order='4321')
        ])

        # Create test data
        data = {'value': np.array([0x12345678, 0xAABBCCDD])}

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['value'], data['value'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_custom_byte_order_2143(self):
        """Test encoding with custom byte order 2143."""
        # Create packet with custom byte order
        packet = FixedLength([
            PacketField(name='value', data_type='uint', bit_length=32, byte_order='2143')
        ])

        # Create test data
        data = {'value': np.array([0x12345678, 0xAABBCCDD, 0x11223344])}

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['value'], data['value'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_array_little_endian(self):
        """Test encoding PacketArray with little endian."""
        # Create packet with array field
        packet = FixedLength([
            PacketArray(
                name='data',
                data_type='uint',
                bit_length=16,
                array_shape=4,
                byte_order='little'
            )
        ])

        # Create test data
        data = {
            'data': np.array([
                [0x1234, 0x5678, 0x9ABC, 0xDEF0],
                [0xAAAA, 0xBBBB, 0xCCCC, 0xDDDD]
            ])
        }

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['data'], data['data'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_multiple_fields_mixed_byte_order(self):
        """Test encoding with multiple fields having different byte orders."""
        # Create packet with mixed byte orders
        packet = FixedLength([
            PacketField(name='big_val', data_type='uint', bit_length=32, byte_order='big'),
            PacketField(name='little_val', data_type='uint', bit_length=32, byte_order='little'),
            PacketField(name='custom_val', data_type='uint', bit_length=32, byte_order='4321'),
        ])

        # Create test data
        data = {
            'big_val': np.array([0x12345678, 0xAABBCCDD]),
            'little_val': np.array([0x11223344, 0x55667788]),
            'custom_val': np.array([0xABCDEF12, 0x13579BDF]),
        }

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['big_val'], data['big_val'])
            np.testing.assert_array_equal(result['little_val'], data['little_val'])
            np.testing.assert_array_equal(result['custom_val'], data['custom_val'])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestEncodeByteOrderVariableLength:
    """Test byte order encoding with VariableLength packets."""

    def test_encode_variable_length_little_endian(self):
        """Test encoding VariableLength packet with little endian."""
        # Create packet with little endian expanding array
        packet = VariableLength([
            PacketField(name='count', data_type='uint', bit_length=8),
            PacketArray(
                name='data',
                data_type='uint',
                bit_length=32,
                array_shape='expand',
                byte_order='little'
            )
        ])

        # Create test data with variable length arrays
        data = {
            'count': np.array([3, 2]),
            'data': np.array([
                np.array([0x12345678, 0xAABBCCDD, 0x11223344], dtype=np.uint32),
                np.array([0x55667788, 0x99AABBCC], dtype=np.uint32)
            ], dtype=object)
        }

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            np.testing.assert_array_equal(result['count'], data['count'])
            for i in range(len(data['data'])):
                np.testing.assert_array_equal(result['data'][i], data['data'][i])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_encode_variable_length_custom_byte_order(self):
        """Test encoding VariableLength packet with custom byte order."""
        # Create packet with custom byte order expanding array
        packet = VariableLength([
            PacketArray(
                name='data',
                data_type='uint',
                bit_length=32,
                array_shape='expand',
                byte_order='4321'
            )
        ])

        # Create test data
        data = {
            'data': np.array([
                np.array([0x12345678, 0xAABBCCDD], dtype=np.uint32),
                np.array([0x11223344], dtype=np.uint32)
            ], dtype=object)
        }

        # Encode to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_file = f.name

        try:
            packet.to_file(temp_file, pkt_type=0, apid=100, sec_header_flag=0, seq_flag=0, data=data)

            # Decode and verify round-trip
            result = packet.load(temp_file)
            for i in range(len(data['data'])):
                np.testing.assert_array_equal(result['data'][i], data['data'][i])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
