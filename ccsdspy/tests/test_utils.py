"""Tests for the ccsdspy.utils packate

Tests for utils.split_by_apid() can be found in test_split.py
"""
import glob
import io
import os

import numpy as np
import pytest

from .. import utils

def test_count_packets_missing_bytes():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    num_packets, missing_bytes = utils.count_packets(tlm_path, return_missing_bytes=True)
    assert missing_bytes == 0


    total_in_split = 0

    for apid, apid_stream in utils.split_by_apid(tlm_path).items():
        total_in_split += utils.count_packets(apid_stream)

    assert total_in_split == num_packets
            

def test_count_packets_simple():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    assert 101 == utils.count_packets(tlm_path)


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


def test_read_packet_bytes_issues_warning():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    with open(tlm_path, "rb") as fh:
        file_bytes = fh.read()

    file_bytes = file_bytes[:-5]  # make last packet be incomplete

    with pytest.warns(UserWarning):
        result = utils.read_packet_bytes(io.BytesIO(file_bytes))


def test_read_packet_bytes_file_like_obj():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    result_1 = utils.read_packet_bytes(tlm_path)

    with open(tlm_path, "rb") as fh:
        result_2 = utils.read_packet_bytes(fh)

    with open(tlm_path, "rb") as fh:
        result_3 = utils.read_packet_bytes(io.BytesIO(fh.read()))

    results = [result_1, result_2, result_3]

    # check deep equality
    assert np.unique([len(res) for res in results]).size == 1

    for i in range(len(results[0])):
        for result in results:
            assert result[i] == results[0][i]


@pytest.mark.parametrize("include_primary_header", [True, False])
def test_read_packet_bytes_mixed_stream(include_primary_header):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    tlm_path = os.path.join(data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first101pkts.tlm")

    header_arrays = utils.read_primary_headers(tlm_path)

    expected_lens = header_arrays["CCSDS_PACKET_LENGTH"] + 1
    if include_primary_header:
        expected_lens += 6

    packet_bytes = utils.read_packet_bytes(tlm_path, include_primary_header=include_primary_header)

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
