"""Tests for the ccsdspy.converters module"""

import os

import numpy as np
import pytest

from .. import converters
from .. import FixedLength, VariableLength, PacketField

TEST_FILENAME = "ccsds_converters_test.bin"


def test_converter_cannot_be_instantiated():
    with pytest.raises(NotImplementedError):
        converters.Converter()


def test_custom_class_with_missing_convert_one():
    class Test(converters.Converter):
        def __init__(self):
            pass

    with pytest.raises(NotImplementedError):
        Test().convert_many(np.arange(10))


@pytest.mark.parametrize("do_2darray", [False, True])
def test_poly_converter_direct_simple(do_2darray):
    coeffs = [0.3, 0.08, 5.4]

    if do_2darray:
        field_array = np.arange(200, dtype=int).reshape(5, 40)
    else:
        field_array = np.arange(10, dtype=int)

    x = field_array.astype(np.float64)
    expected = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
    got = converters.PolyConverter(coeffs).convert_many(field_array)

    assert np.allclose(got, expected)


@pytest.mark.parametrize("do_2darray", [False, True])
def test_linear_converter_direct_simple(do_2darray):
    slope, intercept = 1.2, 0.4

    if do_2darray:
        field_array = np.arange(200, dtype=int).reshape(5, 40)
    else:
        field_array = np.arange(10, dtype=int)
    field_array = np.arange(10, dtype=int)

    x = field_array.astype(np.float64)
    expected = slope * x + intercept
    got = converters.LinearConverter(slope, intercept).convert_many(field_array)

    assert np.allclose(got, expected)


@pytest.mark.parametrize("do_2darray", [False, True])
def test_enum_converter_direct_happy_path(do_2darray):
    replace_dict = {0: "OFF", 1: "ON", 2: "STANDBY", 3: "EMERGENCY"}

    field_array = np.array([0, 3, 1, 1, 3, 2])
    expected = np.array(["OFF", "EMERGENCY", "ON", "ON", "EMERGENCY", "STANDBY"])

    if do_2darray:
        shape = (3, 2)
        field_array = field_array.reshape(shape)
        expected = expected.reshape(shape)

    got = converters.EnumConverter(replace_dict).convert_many(field_array)

    assert np.all(got == expected)


@pytest.mark.parametrize("do_2darray", [False, True])
def test_enum_converter_direct_missing_key(do_2darray):
    replace_dict = {0: "OFF", 1: "ON", 2: "STANDBY", 3: "EMERGENCY"}

    # 8 is the missing value
    field_array = np.array([0, 4, 1, 1, 3, 2])
    expected = np.array(["OFF", "EMERGENCY", "ON", "ON", "EMERGENCY", "STANDBY"])

    if do_2darray:
        shape = (3, 2)
        field_array = field_array.reshape(shape)
        expected = expected.reshape(shape)

    with pytest.raises(converters.EnumConverterMissingKey):
        got = converters.EnumConverter(replace_dict).convert_many(field_array)


def _create_simple_ccsds_packet(n=1):
    packet_version_number = int("000", 2)
    packet_type = int("0", 2)
    secondary_header_flag = int("0", 2)
    apid = 10
    sequence_flag = 1
    packet_counter = 0
    packet_data_length = 4

    CCSDS_PRIMARY_HEADER_LENGTH = 3
    total_packet_length = CCSDS_PRIMARY_HEADER_LENGTH + packet_data_length

    packet = np.zeros(total_packet_length * n, dtype=">u2")

    for i in range(n):
        packet[0 + i * total_packet_length] = (
            (packet_version_number << 13)
            + (packet_type << 12)
            + (secondary_header_flag << 11)
            + apid
        )
        packet[1 + i * total_packet_length] = (sequence_flag << 14) + packet_counter + i
        packet[2 + i * total_packet_length] = (
            packet_data_length * 2 - 1
        )  # packet length in octets minus 2

        packet[3 + i * total_packet_length] = i % 3
        packet[4 + i * total_packet_length] = i % 5
        packet[6 + i * total_packet_length] = i % 10

    packet.tofile(TEST_FILENAME)
    return packet


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_end_to_end(cls):
    num_packets = 75
    packet = _create_simple_ccsds_packet(num_packets)  # noqa: F841

    coeffs = [0.52, 0.1]
    slope, intercept = 5.2, 1.2

    boo_conv = converters.EnumConverter({0: "NO", 1: "YES", 2: "MAYBE"})
    foo_conv = converters.LinearConverter(slope, intercept)
    blah_conv = converters.PolyConverter(coeffs)

    pkt = cls(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16, converter=boo_conv),
            PacketField(name="FOO", data_type="uint", bit_length=16, converter=foo_conv),
            PacketField(name="BLAH", data_type="uint", bit_length=32, converter=blah_conv),
        ]
    )

    result = pkt.load(TEST_FILENAME)

    assert np.all(result["BOO"] == np.array(["NO", "YES", "MAYBE"] * (num_packets // 3)))
    assert np.all(result["FOO"] == (np.arange(num_packets, dtype=int) % 5) * slope + intercept)
    assert np.allclose(
        result["BLAH"], (np.arange(num_packets, dtype=int) % 10) * coeffs[0] + coeffs[1]
    )

    os.remove(TEST_FILENAME)
