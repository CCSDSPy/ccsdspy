"""Create simple packets with variable lengths"""
import struct

import numpy as np

out_name = "var_length_packets_double_varfield_with_footer.bin"
include_footer = True
num_packets = 10
AP_ID = 0x08E2
PACKET_ID = int("0001100000000000", 2) + AP_ID

packet = b""

data1_length = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
data2_length = [5, 7, 2, 8, 3, 41, 42, 1, 3, 4]

assert len(data1_length) == num_packets
assert len(data2_length) == num_packets


for packet_num in range(num_packets):
    # Determine packet length
    packet_length = 0
    packet_length += 1
    packet_length += 2 * data1_length[packet_num]
    packet_length += 1
    packet_length += 2 * data2_length[packet_num]
    packet_length += -1

    if include_footer:
        packet_length += 2

    # Add packet header
    this_packet = struct.pack(">HHH", PACKET_ID, packet_num, packet_length)

    #  data1 array contents start with the array size value and increment by one (e.g. [2, 3], [3, 4, 5]) # noqa: E501
    this_packet += struct.pack("B", data1_length[packet_num])
    for j in range(data1_length[packet_num]):
        this_packet += struct.pack(">H", data1_length[packet_num] + j)

    #  data2 array contents start with the zero and increment to the data2_length
    this_packet += struct.pack("B", data2_length[packet_num])
    for j in range(data2_length[packet_num]):
        this_packet += struct.pack(">H", j)

    # Footer is two bytes at the end
    if include_footer:
        this_packet += struct.pack(">H", 1)

    print(f"packet #{packet_num}: {np.frombuffer(this_packet, dtype='uint8')}")
    packet += this_packet

if include_footer:
    expected_length = (
        8 * num_packets + 2 * np.sum(data1_length) + 2 * np.sum(data2_length) + 2 * num_packets
    )
else:
    expected_length = (
        6 * num_packets + 2 * np.sum(data1_length) + 2 * np.sum(data2_length) + 2 * num_packets
    )

print(f"File length is {len(packet)}. Expected length is {expected_length}.")

f = open(out_name, "wb")
f.write(packet)
f.close()
