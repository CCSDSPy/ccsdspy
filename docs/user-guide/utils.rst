.. _utils:

*********
Utilities
*********

This package provides a number of utilities to work with CCSDS packets.

.. contents::
   :depth: 2

Iterating through Packet Bytes
==============================
During debugging it is often useful to break a stream of multiple packets into a list of byte sequences associated with each packet. That is, the i'th element of the list will be a `bytes` object associated with the i'th packet in the file.

This can be done with the `utils.split_packet_bytes()` (returns a list) and `utils.iter_packet_bytes()` (returns a generator) functions. These functions have an optional keyword argument `include_primary_header=True` which determines whether the primary header is included in the byte sequence returned. By default, it is included.

This function works with mixed files containing multiple APIDs, which may include both fixed length and variable length packets.

.. code-block:: python

  from ccsdspy.utils import split_packet_bytes

  packet_bytes = split_packet_bytes('mixed_file.tlm')

  # Print bytes of first five packets
  for i in range(5):
    print(packet_bytes[i].hex())


This generates the following output for a sequence of variable length packets:

.. code-block::

  20e20000000300020003
  20e200010005000300040005
  20e20002000900050006000700080009
  20e20003000d000700080009000a000b000c000d
  20e200040015000b000c000d000e000f001000110012001300140015


Counting Number of Packets in a File
====================================
Sometimes, it is desirable to know  the number of packets in a file. For this, the `utils.count_packets()` function can be used. It's argument is a file-like object or name of a file. It accepts the optional arguments `return_missing_bytes=True` which can be used to determine the number of bytes which would be needed to be added to the file to complete the last packet (computed using the packet length set in the primary header of last packet).

This function works with mixed files containing multiple APIDs, which may include both fixed length and variable length packets. When used with multiple APIDs, it simply returns the total number of packets of any APID. 


.. code-block:: python

  from ccsdspy.utils import count_packets

  num_packets, missing_bytes = count_packets(
    'mixed_file.tlm',
    return_missing_bytes=True
  )

  print(f"There are {num_packets} complete packets in this file")

  if missing_bytes > 0:
     print(f"The last packet is incomplete. {missing_bytes} bytes "
           "would need to be added to complete the last packet")

  
Splitting Mixed Streams by APID
===============================
Often, CCSDS data will arrive from external sources into software systems in a single file with multiple APIDs.
Splitting a mixed file or stream of bytes by APID so they can be used with the `ccsdspy.FixedLength` class can be done through the API or with the module command line interface.

The API method:

.. code-block:: python

  from ccsdspy.utils import split_by_apid

  with open('mixed_file.tlm', 'rb') as mixed_file:
      # dictionary mapping integer apid to BytesIO
      stream_by_apid = split_by_apid(mixed_file)

The command line interface method:
  
.. code-block::

   $ python -m ccsdspy split mixed_file.tlm
   Parsing done!
   Writing ./apid00132.tlm...
   Writing ./apid00134.tlm...
   Writing ./apid00258.tlm...
   Writing ./apid00384.tlm...
   Writing ./apid00385.tlm...
   Writing ./apid00386.tlm...
   Writing ./apid00387.tlm...


Reading Just Primary Headers
============================
The `utils.read_primary_headers()` function is a utility to read the primary header without providing a packet definition. When decoding an entire packet (including the body), the preferred method is through `pkt.load(include_primary_header=True)`.

This function will return a dictionary mapping header names to a NumPy arrays with a length equal to the number of packets in the file. The header names (keys) are: `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`, `CCSDS_SECONDARY_FLAG`, `CCSDS_SEQUENCE_FLAG`, `CCSDS_APID`, `CCSDS_SEQUENCE_COUNT`, `CCSDS_PACKET_LENGTH`.

This function works with mixed files containing multiple APIDs, which may include both fixed length and variable length packets.

.. code-block:: python

  from ccsdspy.utils import read_primary_headers

  header_arrays = read_primary_headers('mixed_file.tlm')

  # Print APIDs of first five packets
  for i in range(5):
    print(f"Packet {i+1} has APID {header_arrays['CCSDS_APID'][i]}")


The output of this code block is:

.. code-block::

  Packet 1 has APID 391
  Packet 2 has APID 393
  Packet 3 has APID 392
  Packet 4 has APID 394
  Packet 5 has APID 393
