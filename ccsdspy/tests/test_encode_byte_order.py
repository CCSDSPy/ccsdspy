"""Tests for byte order support in encoding.

These tests verify that packets can be encoded with various byte orders
(big, little, custom) and then decoded back correctly.
"""

import os
import tempfile

import numpy as np
import pytest

from ccsdspy import FixedLength, VariableLength, PacketField, PacketArray

# Test byte orders matching those in test_byte_order.py
# Covers all byte lengths from 1 to 8 bytes
TEST_BYTE_ORDERS = {
    1: ["1"],
    2: ["12", "21"],
    3: ["123", "321"],
    4: ["1234", "2143", "3412", "4321"],
    6: ["123456"],
    7: ["1234567"],
    8: ["12345678", "78563412", "87654321"],
}


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


class TestEncodeByteOrderComprehensive:
    """Comprehensive byte order encoding tests matching decode test coverage."""

    @pytest.mark.parametrize(
        "byte_order",
        [
            pytest.param(order, id=f"byteorder_{order}")
            for orders in TEST_BYTE_ORDERS.values()
            for order in orders
        ],
    )
    def test_encode_all_byte_orders_uint(self, byte_order):
        """Test encoding with all byte orders for unsigned integers.

        Mirrors the comprehensive coverage in test_byte_order.py.
        Tests various byte lengths (1, 2, 3, 4, 6, 7, 8 bytes).
        """

        # Calculate bit length from byte order string length
        num_bytes = len(byte_order)
        bit_length = num_bytes * 8

        # Create packet with array field using the byte order
        packet = FixedLength([
            PacketArray(
                name='data',
                data_type='uint',
                bit_length=bit_length,
                array_shape=10,  # Array of 10 elements
                byte_order=byte_order
            )
        ])

        # Generate test data - random values within valid range
        np.random.seed(42)  # Reproducible tests
        # Generate random values and mask to fit within bit_length
        test_values = np.random.randint(0, 2 ** 62, size=(5, 10), dtype=np.uint64)
        # Mask to ensure values fit within the specified bit length
        if bit_length < 64:
            mask = (1 << bit_length) - 1
            test_values = test_values & mask

        # Create test data dictionary
        data = {'data': test_values}

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

    @pytest.mark.parametrize(
        "byte_order",
        [
            pytest.param(order, id=f"byteorder_{order}")
            # Exclude non-power-of-2 byte lengths (3, 6, 7) - decode doesn't support signed int for these
            for byte_length, orders in TEST_BYTE_ORDERS.items()
            if byte_length in (1, 2, 4, 8)
            for order in orders
        ],
    )
    def test_encode_all_byte_orders_int(self, byte_order):
        """Test encoding with all byte orders for signed integers.

        Tests both positive and negative values with various byte orders.
        Only tests power-of-2 byte lengths (1, 2, 4, 8) as decode doesn't
        support signed integers with non-power-of-2 byte lengths.
        """
        num_bytes = len(byte_order)
        bit_length = num_bytes * 8

        # Create packet with array field using the byte order
        packet = FixedLength([
            PacketArray(
                name='data',
                data_type='int',
                bit_length=bit_length,
                array_shape=10,
                byte_order=byte_order
            )
        ])

        # Generate test data - mix of positive and negative values
        np.random.seed(42)
        # Generate random values and adjust to fit within bit_length
        test_values = np.random.randint(-(2 ** 61), 2 ** 61, size=(5, 10), dtype=np.int64)
        # For smaller bit lengths, clamp values to fit
        if bit_length < 64:
            max_val = 2 ** (bit_length - 1) - 1
            min_val = -(2 ** (bit_length - 1))
            test_values = np.clip(test_values, min_val, max_val)

        # Create test data dictionary
        data = {'data': test_values}

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

    @pytest.mark.parametrize(
        "byte_order",
        [
            pytest.param(order, id=f"byteorder_{order}")
            # Exclude non-power-of-2 byte lengths (3, 6, 7) - decode has issues with variable length
            for byte_length, orders in TEST_BYTE_ORDERS.items()
            if byte_length in (1, 2, 4, 8)
            for order in orders
        ],
    )
    def test_encode_all_byte_orders_variable_length(self, byte_order):
        """Test encoding with all byte orders for VariableLength packets.

        Only tests power-of-2 byte lengths (1, 2, 4, 8) as decode has issues
        with variable length for non-power-of-2 byte lengths.
        """
        num_bytes = len(byte_order)
        bit_length = num_bytes * 8

        # Create variable length packet with expanding array
        packet = VariableLength([
            PacketArray(
                name='data',
                data_type='uint',
                bit_length=bit_length,
                array_shape='expand',
                byte_order=byte_order
            )
        ])

        # Generate test data with variable length arrays
        np.random.seed(42)
        # Generate random values and mask to fit within bit_length
        arr1 = np.random.randint(0, 2 ** 62, size=5, dtype=np.uint64)
        arr2 = np.random.randint(0, 2 ** 62, size=8, dtype=np.uint64)
        arr3 = np.random.randint(0, 2 ** 62, size=3, dtype=np.uint64)
        # Mask to ensure values fit within the specified bit length
        if bit_length < 64:
            mask = (1 << bit_length) - 1
            arr1 = arr1 & mask
            arr2 = arr2 & mask
            arr3 = arr3 & mask
        test_data = np.array([arr1, arr2, arr3], dtype=object)

        data = {'data': test_data}

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
