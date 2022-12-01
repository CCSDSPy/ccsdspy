import numpy as np
import os

from .. import FixedLength, PacketField

TEST_FILENAME = "ccsds_test.bin"


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
        )  # packet lenght in octets minus 2

        packet[3 + i * total_packet_length] = 314
        packet[4 + i * total_packet_length] = 512
        packet[6 + i * total_packet_length] = 10000

    packet.tofile(TEST_FILENAME)
    return packet


def test_primary_header_contents_no_offset():
    """Test if the primary header is output correctly along with the data without defining bit offsets"""
    num_packets = 3
    packet = create_simple_ccsds_packet(num_packets)

    pkt = FixedLength(
        [
            PacketField(name="BOO", data_type="uint", bit_length=16),
            PacketField(name="FOO", data_type="uint", bit_length=16),
            PacketField(name="BLAH", data_type="uint", bit_length=32),
        ]
    )

    result = pkt.load("ccsds_test.bin", include_primary_header=True)
    assert (result["CCSDS_VERSION_NUMBER"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_PACKET_TYPE"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SECONDARY_FLAG"] == np.zeros(num_packets, dtype="uint")).all()
    assert (result["CCSDS_APID"] == 10 * np.ones(num_packets, dtype="uint")).all()
    assert (result["CCSDS_SEQUENCE_FLAG"] == np.ones(num_packets, dtype="uint")).all()
    assert (
        result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")
    ).all()
    assert (
        result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")
    ).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)


def test_primary_header_contents_offset():
    """Test if the primary header is output correctly along with the data with defining bit offsets"""
    num_packets = 3
    packet = create_simple_ccsds_packet(num_packets)

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
    assert (
        result["CCSDS_SEQUENCE_COUNT"] == np.arange(num_packets, dtype="uint")
    ).all()
    assert (
        result["CCSDS_PACKET_LENGTH"] == 7 * np.ones(num_packets, dtype="uint")
    ).all()
    assert (result["BOO"] == 314 * np.ones(num_packets, dtype="uint")).all()
    assert (result["FOO"] == 512 * np.ones(num_packets, dtype="uint")).all()
    assert (result["BLAH"] == 10000 * np.ones(num_packets, dtype="uint")).all()
    os.remove(TEST_FILENAME)
