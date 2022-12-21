"""Create simple packets with variable lengths"""
import struct

import numpy as np

num_packets = 10
AP_ID = 0x08E2
PACKET_ID = int("0001100000000000", 2) + AP_ID

packet = b""

data_length = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

for packet_num in range(num_packets):
    packet_length = 2 * data_length[packet_num] - 1
    this_packet = struct.pack(">HHH", PACKET_ID, packet_num, packet_length)

    for j in range(data_length[packet_num]):
        this_packet += struct.pack(">H", data_length[packet_num] + j)
    print(f"packet #{packet_num}: {np.frombuffer(this_packet, dtype='uint8')}")
    packet += this_packet

expected_length = 6 * num_packets + 2 * np.sum(data_length)
print(f"Packet length is {len(packet)}. Expected length is {expected_length}.")

f = open("var_length_packets.bin", "wb")
f.write(packet)
f.close()
