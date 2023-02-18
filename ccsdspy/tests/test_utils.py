"""Tests for the ccsdspy.utils packate

Tests for utils.split_by_apid() can be found in test_split.py
"""
import os

import numpy as np

from .. import utils


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

        assert np.all(header_arrays['CCSDS_VERSION_NUMBER'] == 0)
        assert np.all(header_arrays['CCSDS_PACKET_TYPE'] == 0)
        assert np.all(header_arrays['CCSDS_SECONDARY_FLAG'] == 1)
        assert np.all(header_arrays['CCSDS_SEQUENCE_FLAG'] == 3)
        assert np.all(header_arrays['CCSDS_APID'] == apid)
        assert np.all(np.diff(header_arrays['CCSDS_SEQUENCE_COUNT']) > 0)
        assert np.unique(header_arrays['CCSDS_PACKET_LENGTH']).size == 1  # fixed length
 
