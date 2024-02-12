
import numpy as np
import struct

np.random.seed(0)

# Obtained from github discusison #110
TEST_BYTE_ORDERS = {
    1: ["1"],
    2: ["12", "21"],
    3: ["123", "321"],
    4: ["1234", "2143", "3412", "4321"],
    6: ["123456"],
    7: ["1234567"],
    8: ["12345678", "78563412", "87654321"],    
}

NUM_PACKETS = 10
PACKET_ARRAY_LENGTH = 80

def main():
    for _, byte_order_list in TEST_BYTE_ORDERS.items():
        for byte_order in byte_order_list:
            print(f"Byte Order: {byte_order}")
            write_packet(byte_order)


def write_packet(byte_order):
    bin_fname = f'byteorder_{byte_order}.bin'
    csv_fname = f'byteorder_{byte_order}.csv'
    apid = 0x08E2
    packet_id = int("0001100000000000", 2) + apid
    file_bytes = b""
    csv_lines = []
    
    for i in range(NUM_PACKETS):
        packet_length = len(byte_order) * PACKET_ARRAY_LENGTH - 1    
        this_packet = struct.pack(">HHH", packet_id, i, packet_length)
        
        array = np.random.randint(low=0, high=2**(8*len(byte_order)) - 1,
                                  size=PACKET_ARRAY_LENGTH, 
                                  dtype=np.uint64)

        array_bytes = array.copy()
        array_bytes.dtype = np.uint8
        array_bytes = array_bytes.reshape((array.size, 8))
        
        for j in range(PACKET_ARRAY_LENGTH):
            cur_bytes = [array_bytes[j, int(byte_num) - 1]
                         for byte_num in byte_order]
            cur_bytes.reverse()
            for b in cur_bytes:
                this_packet += struct.pack("B", b)
                
        file_bytes += this_packet
        csv_lines.append(",".join(map(str, array.tolist())) + "\n")
        
    expected_length = 6 * NUM_PACKETS + len(byte_order) * NUM_PACKETS * PACKET_ARRAY_LENGTH
    print(f"  Packet length is {len(file_bytes)}. Expected length is {expected_length}.")

    with open(bin_fname, "wb") as bin_fh:
        bin_fh.write(file_bytes)

    print(f"  Wrote {bin_fname}")
    
    with open(csv_fname, "w") as csv_fh:
        csv_fh.writelines(csv_lines)

    print(f"  Wrote {csv_fname}")

if __name__ == '__main__':
    main()
