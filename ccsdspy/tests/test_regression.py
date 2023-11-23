"""Regression Tests"""

import io
import os

import numpy as np
import pytest

from .. import FixedLength, VariableLength, PacketField, PacketArray


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


@pytest.mark.parametrize("pkt_class", [FixedLength, VariableLength])
def test_nbytes_file_too_long(pkt_class):
    """This fixes an issue where nbytes_file was incorrectly incremented
    and sometimes reaches past the end of the file.

    See: https://github.com/CCSDSPy/ccsdspy/issues/78
    """

    # Create packet definition
    pkt = pkt_class(
        [
            PacketArray(
                name="twelve", data_type="int", bit_length=12, array_shape=(8, 1), array_order="C"
            )
        ]
    )

    # Test with one packets
    fakepkt = io.BytesIO(
        b"\x00\x01\xC0\x00\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07"
    )

    with open("fake_twelve_single.ccsds", "wb") as file:
        file.write(fakepkt.getbuffer())

    result = pkt.load(fakepkt)

    assert result["twelve"].shape == (1, 8, 1)
    assert np.array_equal(result["twelve"], np.arange(8).reshape((1, 8, 1)))

    # Test with two packets
    fakepkts_even = io.BytesIO(
        b"\x00\x01\xC0\x01\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07\x00\x01\xC0\x02\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07"
    )

    with open("fake_twelve_even.ccsds", "wb") as file:
        file.write(fakepkts_even.getbuffer())

    result = pkt.load(fakepkts_even)

    expected = np.array([np.arange(8), np.arange(8)]).reshape(2, 8, 1)

    assert result["twelve"].shape == (2, 8, 1)
    assert np.array_equal(result["twelve"], expected)

    # Test with three packets
    fakepkts_odd = io.BytesIO(
        b"\x00\x01\xC0\x01\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07\x00\x01\xC0\x02\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07\x00\x01\xC0\x03\x00\x0B\x00\x00\x01\x00\x20\x03\x00\x40\x05\x00\x60\x07"
    )

    with open("fake_twelve_odd.ccsds", "wb") as file:
        file.write(fakepkts_odd.getbuffer())

    result = pkt.load(fakepkts_odd)

    expected = np.array([np.arange(8), np.arange(8), np.arange(8)]).reshape(3, 8, 1)

    assert result["twelve"].shape == (3, 8, 1)
    assert np.array_equal(result["twelve"], expected)


@pytest.mark.parametrize("pkt_class", [FixedLength, VariableLength])
def test_neg_ints_flip_start_bit(pkt_class):
    """This fixes an issue where flipping the padding bits was done
    from the incorrect start bit.

    See: https://github.com/CCSDSPy/ccsdspy/issues/80
    """
    pkt = pkt_class(
        [
            PacketField(name="uinttwo", data_type="uint", bit_length=3),
            PacketField(name="negfive", data_type="int", bit_length=5),
            PacketField(name="postwelve", data_type="int", bit_length=12),
            PacketField(name="negsix", data_type="int", bit_length=12),
        ]
    )

    # 0b101, 0b11011, 0b000000001100, 0b111111110100
    fakepkt = io.BytesIO(b"\x00\x01\xC0\x00\x00\x03\x5B\x00\xCF\xFA")
    result = pkt.load(fakepkt)

    assert np.array_equal(result["uinttwo"], np.array([2], dtype=np.uint8))
    assert np.array_equal(result["negfive"], np.array([-5], dtype=np.int8))
    assert np.array_equal(result["postwelve"], np.array([12], dtype=np.int16))
    assert np.array_equal(result["negsix"], np.array([-6], dtype=np.int16))


def test_expand_with_footer_bits():
    """This fixes an issue where expanding field length is not calculated correctly
    when fields follow it.

    See: https://github.com/CCSDSPy/ccsdspy/discussions/102
    """
    pkt = VariableLength(
        [
            PacketField(name="Instrument SCLK Time second", bit_length=32, data_type="uint"),
            PacketField(name="Instrument SCLK Time subsec", bit_length=16, data_type="uint"),
            PacketField(name="Accountability ID", bit_length=32, data_type="uint"),
            PacketArray(name="FGX_CHANNELS", data_type="uint", bit_length=8, array_shape="expand"),
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
    bin_path = os.path.join(dir_path, "data", "europa_clipper", "expanding_footer_packet.bin")

    results = pkt.load(bin_path)

    for arr in results["FGX_CHANNELS"]:
        assert arr.shape == (1440,)
