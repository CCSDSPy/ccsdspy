import numpy as np
import os

import pytest

from .. import FixedLength, VariableLength, PacketField
from ..packet_types import _inspect_primary_header_fields

TEST_FILENAME = "ccsds_primary_headers_test.bin"


def create_simple_ccsds_packet(n=1):
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

        packet[3 + i * total_packet_length] = 314
        packet[4 + i * total_packet_length] = 512
        packet[6 + i * total_packet_length] = 10000

    packet.tofile(TEST_FILENAME)
    return packet


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_primary_header_contents_no_offset(cls):
    """Test if the primary header is output correctly along with the data without
    defining bit offsets"""
    num_packets = 3
    create_simple_ccsds_packet(num_packets)  # noqa: F841

    pkt = cls(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16),
            PacketField(name="FOO", data_type="uint", bit_length=16),
            PacketField(name="BLAH", data_type="uint", bit_length=32),
        ]
    )

    result = pkt.load(TEST_FILENAME, include_primary_header=True)
    assert (result["CCSDS_VERSION_NUMBER"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_TYPE"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SECONDARY_FLAG"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_APID"] == 10 * np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_FLAG"] == np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)


def test_primary_header_contents_offset():
    """Test if the primary header is output correctly along with the data with
    defining bit offsets"""
    num_packets = 3
    create_simple_ccsds_packet(num_packets)  # noqa: F841

    pkt = FixedLength(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16, bit_offset=48),
            PacketField(name="FOO", data_type="uint", bit_length=16, bit_offset=64),
            PacketField(name="BLAH", data_type="uint", bit_length=32, bit_offset=80),
        ]
    )

    result = pkt.load(TEST_FILENAME, include_primary_header=True)
    assert (result["CCSDS_VERSION_NUMBER"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_TYPE"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SECONDARY_FLAG"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_APID"] == 10 * np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_FLAG"] == np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)


def test_primary_header_contents_offset():
    """Test if the primary header is output correctly along with the data with
    defining bit offsets"""
    num_packets = 3
    packet = create_simple_ccsds_packet(num_packets)  # noqa: F841

    pkt = FixedLength(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16, bit_offset=48),
            PacketField(name="FOO", data_type="uint", bit_length=16, bit_offset=64),
            PacketField(name="BLAH", data_type="uint", bit_length=32, bit_offset=80),
        ]
    )

    result = pkt.load("ccsds_test.bin", include_primary_header=True)
    assert (result["CCSDS_VERSION_NUMBER"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_TYPE"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SECONDARY_FLAG"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_APID"] == 10 * np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_FLAG"] == np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)


def test_primary_header_contents_offset():
    """Test if the primary header is output correctly along with the data with
    defining bit offsets"""
    num_packets = 3
    packet = create_simple_ccsds_packet(num_packets)  # noqa: F841

    pkt = FixedLength(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16, bit_offset=48),
            PacketField(name="FOO", data_type="uint", bit_length=16, bit_offset=64),
            PacketField(name="BLAH", data_type="uint", bit_length=32, bit_offset=80),
        ]
    )

    result = pkt.load(TEST_FILENAME, include_primary_header=True)
    assert (result["CCSDS_VERSION_NUMBER"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_TYPE"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SECONDARY_FLAG"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_APID"] == 10 * np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_FLAG"] == np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)


def test_check_primary_header_contents_missingseq():
    """Check that non consecutive sequence counts raises a warning."""
    num_packets = 10000
    packet_data = {
        "CCSDS_SEQUENCE_COUNT": np.arange(1, num_packets),
        "CCSDS_APID": 1 * np.ones(num_packets),
    }

    packet_data["CCSDS_SEQUENCE_COUNT"][250] = 0

    # TODO check that the warning states the right missing packets
    with pytest.warns(UserWarning):
        _inspect_primary_header_fields(packet_data)

    packet_data["CCSDS_SEQUENCE_COUNT"][500] = 0

    # TODO check that the warning states the right missing packets
    with pytest.warns(UserWarning):
        # check that it tells you that both 100 and 249 are missing
        _inspect_primary_header_fields(packet_data)


def test_check_primary_header_contents_nonconseq():
    """Check that non consecutive sequence counts raises a warning."""
    num_packets = 10000
    packet_data = {
        "CCSDS_SEQUENCE_COUNT": np.flip(np.arange(1, num_packets)),
        "CCSDS_APID": 1 * np.ones(num_packets),
    }

    with pytest.warns(UserWarning, match="out of order"):
        _inspect_primary_header_fields(packet_data)


def test_check_primary_header_contents_sameapid():
    """Check that all apids are the same."""
    num_packets = 10000
    packet_data = {
        "CCSDS_SEQUENCE_COUNT": np.arange(1, num_packets),
        "CCSDS_APID": 48 * np.ones(num_packets),
    }

    with pytest.warns(UserWarning, match="Found multiple AP IDs"):
        packet_data["CCSDS_APID"][100:200] = 58
        _inspect_primary_header_fields(packet_data)
