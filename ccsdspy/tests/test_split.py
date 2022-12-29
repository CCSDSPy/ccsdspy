import csv
import glob
import os
import shutil
import tempfile

import numpy as np
import pytest

from .. import FixedLength, VariableLength, PacketField
from ..__main__ import module_main
from ..utils import split_by_apid


def test_command_line_split():
    """Tests command line interface to the code"""
    # TemporaryDirectory() will delete itself when its garbage collected
    # or when the program ends
    tmp_dir = tempfile.TemporaryDirectory()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    mixed_stream = os.path.join(
        data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first100pkts.tlm"
    )
    shutil.copy(mixed_stream, tmp_dir.name)

    # Call module_main() with fake argv and custom working directory
    module_main(
        argv=[
            "__tests__",
            "split",
            mixed_stream,
        ],
        cwd=tmp_dir.name,
    )

    # Check files in output directory
    expected_files = [
        "apid00384.tlm",
        "apid00386.tlm",
        "apid00391.tlm",
        "apid00392.tlm",
        "apid00393.tlm",
        "apid00394.tlm",
        "apid01313.tlm",
    ]

    for expected_file in expected_files:
        expected_path = os.path.join(data_path, expected_file)
        got_path = os.path.join(tmp_dir.name, expected_file)

        assert os.path.exists(got_path), got_path

        with open(expected_path, "rb") as fh:
            expected_bytes = fh.read()
        with open(got_path, "rb") as fh:
            got_bytes = fh.read()

        assert expected_bytes == got_bytes


@pytest.mark.parametrize("cls", [FixedLength, VariableLength])
def test_split_by_apid_and_decode(cls):
    # Read each CSV file in the data directory
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "split")
    csv_glob = os.path.join(data_path, "defs", "*.csv")

    csv_tables = {}

    for file_name in glob.glob(csv_glob):
        key = os.path.basename(file_name).replace(".csv", "")

        with open(file_name) as csv_file:
            csv_tables[key] = list(csv.DictReader(csv_file))

    # Create a FixedLength of VariableLength for each packet
    packet_by_apid = {}

    for row_overview in csv_tables["Overview"]:
        pkt_table = csv_tables[row_overview["Packet Short Name"]]
        apid = int(row_overview["APID_Decimal"])
        fields = []

        for row in pkt_table:
            row_mnemonic = row["Mnemonic       "]
            row_data_type = row["Type           "]
            row_data_size = int(row["Data Size"])

            if "FILL" in row_mnemonic.upper().strip():
                data_type = "fill"
            elif row_data_type[0] == "U":
                data_type = "uint"
            elif row_data_type[0] == "F":
                data_type = "float"
            elif row_data_type[0] == "I":
                data_type = "int"
            else:
                raise RuntimeError(row_data_type)

            if len(row_data_type) > 2:
                if int(row_data_type[1]) > int(row_data_type[2]):
                    byte_order = "little"
                else:
                    byte_order = "big"
            else:
                byte_order = "big"

            bit_length = row_data_size

            field = PacketField(
                name=row_mnemonic,
                data_type=data_type,
                bit_length=bit_length,
                byte_order=byte_order,
            )
            fields.append(field)

        # drop first seven because are they primary header
        packet_by_apid[apid] = cls(fields[7:])

    # Do split and test result to ground truth
    mixed_stream = os.path.join(
        data_path, "CYGNSS_F7_L0_2022_086_10_15_V01_F__first100pkts.tlm"
    )
    stream_by_apid = split_by_apid(
        mixed_stream, valid_apids=list(packet_by_apid.keys())
    )

    for apid, stream_from_split in stream_by_apid.items():
        if apid in [132, 134, 389, 391]:
            # Known to have problems for acceptable reasons (insufficient packet definition)
            continue

        split_result = packet_by_apid[apid].load(
            stream_from_split,
        )

        truth_file = os.path.join(data_path, f"apid{str(apid).zfill(5)}.tlm")
        true_result = packet_by_apid[apid].load(truth_file)

        assert list(split_result.keys()) == list(true_result.keys())

        for key in split_result:
            assert np.all(split_result[key] == true_result[key])
