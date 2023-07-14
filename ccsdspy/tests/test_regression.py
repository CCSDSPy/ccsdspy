"""Regression Tests"""

import os

import numpy as np
import pytest

from .. import FixedLength, VariableLength, PacketField


@pytest.mark.parametrize("pkt_class", [FixedLength, VariableLength])
def test_odd_length_neg_ints(pkt_class):
    """This fixes an issue with odd-length integers being negative (odd length
     meaning something like 24 bit).

    See: https://github.com/CCSDSPy/ccsdspy/issues/76
    """
    # This will parse the apid=1227 packet. Code obtained from @nischayn99 created
    # the definition dynamically, so repeating that here.
    TIME_SAMPLE_PER_HF_PACKET = 160

    fields = [
        PacketField(name="Instrument SCLK Time second", bit_length=32, data_type="uint"),
        PacketField(name="Instrument SCLK Time subsec", bit_length=16, data_type="uint"),
        PacketField(name="Accountability ID", bit_length=32, data_type="uint"),
    ]

    for i in range(TIME_SAMPLE_PER_HF_PACKET):
        for c in range(3, 0, -1):
            fields.append(PacketField(f"FGx_CH{c}_{i}", bit_length=24, data_type="int"))

    fields.extend(
        [
            PacketField(name="FGx_-4.7VHK", bit_length=24, data_type="int"),
            PacketField(name="FGx_+4.7VHK", bit_length=24, data_type="int"),
            PacketField(name="FGx_2VREF", bit_length=24, data_type="int"),
            PacketField(name="FGx_1VREF", bit_length=24, data_type="int"),
            PacketField(name="FGx_DRV_SNS", bit_length=24, data_type="int"),
            PacketField(name="FGx_OP_PRTA", bit_length=24, data_type="int"),
            PacketField(name="FGx_FBX", bit_length=24, data_type="int"),
            PacketField(name="FGx_FBY", bit_length=24, data_type="int"),
            PacketField(name="FGx_FBZ", bit_length=24, data_type="int"),
            PacketField(name="FGx_BPFX", bit_length=24, data_type="int"),
            PacketField(name="FGx_BPFY", bit_length=24, data_type="int"),
            PacketField(name="FGx_BPFZ", bit_length=24, data_type="int"),
            PacketField(name="FGx_+4.7_I", bit_length=24, data_type="int"),
            PacketField(name="FGx_-4.7_I", bit_length=24, data_type="int"),
            PacketField(name="FGx_HK_CH14", bit_length=24, data_type="int"),
            PacketField(name="FGx_HK_CH15", bit_length=24, data_type="int"),
            PacketField(name="Register 80", bit_length=16, data_type="uint"),
            PacketField(name="PEC (CRC-16-CCITT)", bit_length=16, data_type="uint"),
        ]
    )

    # Try parsing the packet
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bin_path = os.path.join(dir_path, "data", "europa_clipper", "apid01227.tlm")

    pkt = pkt_class(fields)
    results = pkt.load(bin_path)

    assert np.all(results["FGx_CH1_134"] == -88)
    assert np.issubdtype(results["FGx_CH1_134"].dtype, np.int32)

    assert np.all(results["Accountability ID"] == 400)
    assert np.issubdtype(results["Accountability ID"].dtype, np.uint32)
