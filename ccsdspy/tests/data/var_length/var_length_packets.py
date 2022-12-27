"""Create simple packets with variable lengths"""
import struct

import numpy as np

out_name = "var_length_packets_with_footer.bin"
include_footer = True
num_packets = 10
AP_ID = 0x08E2
PACKET_ID = int("0001100000000000", 2) + AP_ID

packet = b""

data_length = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

for packet_num in range(num_packets):
    packet_length = 2 * data_length[packet_num] - 1
    if include_footer:
        packet_length += 2

    this_packet = struct.pack(">HHH", PACKET_ID, packet_num, packet_length)

    for j in range(data_length[packet_num]):
        this_packet += struct.pack(">H", data_length[packet_num] + j)

    if include_footer:
        this_packet += struct.pack(">H", 1)

    print(f"packet #{packet_num}: {np.frombuffer(this_packet, dtype='uint8')}")
    packet += this_packet

if include_footer:
    expected_length = 8 * num_packets + 2 * np.sum(data_length)
else:
    expected_length = 6 * num_packets + 2 * np.sum(data_length)

print(f"Packet length is {len(packet)}. Expected length is {expected_length}.")

f = open(out_name, "wb")
f.write(packet)
f.close()
