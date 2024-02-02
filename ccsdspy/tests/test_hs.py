"""Run end-to-end test of decoding fixed-length packets
using the test data in the data/hs directory.
"""

import csv
import glob
import os
import numpy as np

import pytest

from .. import FixedLength, VariableLength, PacketField, PacketArray
from ..constants import BITS_PER_BYTE


def _run_apid_test(apid, cls):
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
    _decode_ccsds_file(ccsds_file_path, defs, cls)


def _load_apid_defs(defs_file_path):
    """Load APID definitions (defs.csv) and return a Table"""
    table_dict = {
        "name": [],
        "data_type": [],
        "bit_offset": [],
        "bit_length": [],
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


def _decode_ccsds_file(ccsds_file_path, defs, cls):
    pkt_fields = []

    for key, data_type, bit_length in zip(defs["name"], defs["data_type"], defs["bit_length"]):
        pkt_fields.append(PacketField(name=key, data_type=data_type, bit_length=bit_length))

    # Skip first two, which specify the primary header
    pkt = cls(pkt_fields[2:])
    decoded = pkt.load(ccsds_file_path)

    return decoded


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid001(cls):
    _run_apid_test(1, cls)


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid010(cls):
    _run_apid_test(10, cls)


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid035(cls):
    _run_apid_test(35, cls)


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid130(cls):
    _run_apid_test(130, cls)


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid251(cls):
    _run_apid_test(251, cls)


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_hs_apid895(cls):
    _run_apid_test(895, cls)


def test_hs_apid035_PacketArray():
    # Make FixedLength for normal packet
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apid_dir = os.path.join(dir_path, "data", "hs", "apid035")
    defs_file_path = os.path.join(apid_dir, "defs.csv")
    dict_normal_defs = _load_apid_defs(defs_file_path)

    pkt_fields = []
    tmp = (
        dict_normal_defs["name"],
        dict_normal_defs["data_type"],
        dict_normal_defs["bit_length"],
    )

    for key, data_type, bit_length in zip(*tmp):
        pkt_fields.append(PacketField(name=key, data_type=data_type, bit_length=bit_length))

    normal_pkt = FixedLength(pkt_fields)

    # Make FixedLength for array packet
    fill_length = sum(f._bit_length for f in pkt_fields if "[" not in f._name)

    array_pkt = FixedLength(
        [
            PacketField(name="unused", data_type="fill", bit_length=fill_length),
            PacketArray(name="PKT35_FLT_SIN_2H", data_type="float", bit_length=32, array_shape=8),
        ]
    )

    # Compare data
    ccsds_file_path = glob.glob(os.path.join(apid_dir, "*.tlm")).pop()
    normal_result = normal_pkt.load(ccsds_file_path)
    array_result = array_pkt.load(ccsds_file_path)

    for i in range(8):
        assert np.all(
            normal_result[f"PKT35_FLT_SIN_2H[{i}]"] == array_result["PKT35_FLT_SIN_2H"][:, i]
        )
        # These sin values should be between [0, 1]
        assert np.abs(normal_result[f"PKT35_FLT_SIN_2H[{i}]"].min() - -1.0) < 1e-3
        assert np.abs(normal_result[f"PKT35_FLT_SIN_2H[{i}]"].max() - +1.0) < 1e-3
