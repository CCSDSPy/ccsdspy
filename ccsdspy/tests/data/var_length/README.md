Variable Length Packet
======================

var_length_packets.bin
----------------------
This file was generated by `var_length_packets.py`.
This file contains 10 packets with an AP ID of 0x08E2.
Each packet contains a data field of a variable length.
The data element is a 16 bit unsigned int.
The number of data elements in each packets grows according to the following array, [2, 3, 5, 7, 11, 13, 17, 19, 23,  29].
The data contained in the first element is equal to the number of data elements with each subsequent field increasing by one.
For example, the 4th packet contains the following elements [7, 8, 9, 10, 11, 12, 13].