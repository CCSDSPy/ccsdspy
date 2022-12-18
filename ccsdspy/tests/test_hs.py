"""Run end-to-end test of decoding fixed-length packets
using the test data in the data/hs directory.
"""
import csv
import glob
import json
import os
import numpy as np
from .. import FixedLength, PacketField


def _run_apid_test(apid):
    """Driver for running an APID test. Each apidXXX directory under
    `data/hs` contains:

            defs.csv     -- packet definition with conversions.
            xxxx.tlm     -- binary CCSDS file
    """
    # Setup paths for the definitions, truth, and CCSDS files
    # in the APID directory.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apid_dir = os.path.join(dir_path, "data", "hs", f"apid{apid:03d}")

    defs_file_path = os.path.join(apid_dir, "defs.csv")
    ccsds_file_path = glob.glob(os.path.join(apid_dir, "*.tlm")).pop()

    assert all(
        os.path.exists(path)
        for path in (
            apid_dir,
            defs_file_path,
            ccsds_file_path,
        )
    )

    # Load the definitions, and test that they parse.  We have not prepared
    # a truth reference for this set of test data.
    defs = _load_apid_defs(defs_file_path)
    _decode_ccsds_file(ccsds_file_path, defs)


def _load_apid_defs(defs_file_path):
    """Load APID definitions (defs.csv) and return a Table"""
    table_dict = {
        "name": [],
        "data_type": [],
        "bit_offset": [],
        "bit_length": [],
        "calibration": [],
    }

    # Loop through CSV lines, read all as strings.
    with open(defs_file_path) as fh:
        reader = csv.reader(fh)
        first_line = True

        for row in reader:
            if first_line:
                first_line = False
                continue

            for key, row_value in zip(table_dict.keys(), row):
                table_dict[key].append(row_value)

    # Change from string to final type.
    table_dict["name"] = [name.upper() for name in table_dict["name"]]
    table_dict["bit_offset"] = [int(n) for n in table_dict["bit_offset"]]
    table_dict["bit_length"] = [int(n) for n in table_dict["bit_length"]]

    return table_dict


def _decode_ccsds_file(ccsds_file_path, defs):
    pkt_fields = []

    for key, data_type, bit_length in zip(
        defs["name"], defs["data_type"], defs["bit_length"]
    ):
        pkt_fields.append(
            PacketField(name=key, data_type=data_type, bit_length=bit_length)
        )

    pkt = FixedLength(pkt_fields)
    decoded = pkt.load(ccsds_file_path)

    return decoded


def test_hs_apid001():
    _run_apid_test(1)


def test_hs_apid010():
    _run_apid_test(10)


def test_hs_apid035():
    _run_apid_test(35)


def test_hs_apid130():
    _run_apid_test(130)


def test_hs_apid251():
    _run_apid_test(251)


def test_hs_apid895():
    _run_apid_test(895)
