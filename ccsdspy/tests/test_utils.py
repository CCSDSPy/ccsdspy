"""Tests for the ccsdspy.utils packate

Tests for utils.split_by_apid() can be found in test_split.py
"""
import glob
import io
import os

import numpy as np
import pytest

from ..constants import BITS_PER_BYTE, PRIMARY_HEADER_NUM_BYTES
from .. import utils


def test_count_packets_extra_fields_zero():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    orig_num_packets = utils.count_packets(tlm_path)

    num_packets, missing_bytes, extra_bytes = utils.count_packets(
        tlm_path, return_missing_bytes=True, return_extra_bytes=True
    )
    assert orig_num_packets == num_packets
    assert missing_bytes is None
    assert extra_bytes == 0

    total_in_split = 0

    for apid, apid_stream in utils.split_by_apid(tlm_path).items():
        total_in_split += utils.count_packets(apid_stream)

    assert total_in_split == num_packets


def test_count_packets_extra_fields_nonzero():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")
    extra_added = 15

    byte_stream = io.BytesIO()

    with open(tlm_path, "rb") as fh:
        byte_stream.write(fh.read())

    byte_stream.write(bytes([255] * extra_added))
    byte_stream.seek(0)

    num_packets, missing_bytes, extra_bytes = utils.count_packets(
        byte_stream, return_missing_bytes=True, return_extra_bytes=True
    )
    assert extra_added > PRIMARY_HEADER_NUM_BYTES

    # the last packet set has 1s in all the length bits, therefore the expected length
    # should be 2**16 + !
    assert missing_bytes == 2 ** (BITS_PER_BYTE * 2) + 1 - extra_added + PRIMARY_HEADER_NUM_BYTES
    assert extra_bytes == extra_added


def test_count_packets_simple():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    assert utils.count_packets(tlm_path) == len(list(utils.iter_packet_bytes(tlm_path)))


def test_count_packets_file_like_obj():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    result_1 = utils.count_packets(tlm_path)

    with open(tlm_path, "rb") as fh:
        result_2 = utils.count_packets(fh)

    with open(tlm_path, "rb") as fh:
        result_3 = utils.count_packets(io.BytesIO(fh.read()))

    assert isinstance(result_1, int)
    assert isinstance(result_2, int)
    assert isinstance(result_3, int)

    assert result_1 == result_2
    assert result_1 == result_3


def test_split_packet_bytes_issues_warning():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    with open(tlm_path, "rb") as fh:
        file_bytes = fh.read()

    file_bytes = file_bytes[:-5]  # make last packet be incomplete

    with pytest.warns(UserWarning):
        result = utils.split_packet_bytes(io.BytesIO(file_bytes))


def test_split_packet_bytes_file_like_obj():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    result_1 = utils.split_packet_bytes(tlm_path)

    with open(tlm_path, "rb") as fh:
        result_2 = utils.split_packet_bytes(fh)

    with open(tlm_path, "rb") as fh:
        result_3 = utils.split_packet_bytes(io.BytesIO(fh.read()))

    results = [result_1, result_2, result_3]

    # check deep equality
    assert np.unique([len(res) for res in results]).size == 1

    for i in range(len(results[0])):
        for result in results:
            assert result[i] == results[0][i]


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_split_packet_bytes_mixed_stream(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    header_arrays = utils.read_primary_headers(tlm_path)

    expected_lens = header_arrays["CCSDS_PACKET_LENGTH"] + 1
    if include_primary_header:
        expected_lens += 6

    packet_bytes = utils.split_packet_bytes(tlm_path, include_primary_header=include_primary_header)

    for cur_exp_len, cur_packet_bytes in zip(expected_lens, packet_bytes):
        assert cur_exp_len == len(cur_packet_bytes)


def test_read_primary_headers():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")

    # Check files in output directory
    tlm_files = [
        "apid00384.tlm",
        "apid00386.tlm",
        "apid00391.tlm",
        "apid00392.tlm",
        "apid00393.tlm",
        "apid00394.tlm",
        "apid01313.tlm",
    ]

    for tlm_file in tlm_files:
        tlm_path = os.path.join(data_path, tlm_file)
        header_arrays = utils.read_primary_headers(tlm_path)
        apid = int(tlm_file[4:-4])

        assert np.all(header_arrays["CCSDS_VERSION_NUMBER"] == 0)
        assert np.all(header_arrays["CCSDS_PACKET_TYPE"] == 0)
        assert np.all(header_arrays["CCSDS_SECONDARY_FLAG"] == 1)
        assert np.all(header_arrays["CCSDS_SEQUENCE_FLAG"] == 3)
        assert np.all(header_arrays["CCSDS_APID"] == apid)
        assert np.all(np.diff(header_arrays["CCSDS_SEQUENCE_COUNT"]) > 0)
        assert np.unique(header_arrays["CCSDS_PACKET_LENGTH"]).size == 1  # fixed length
