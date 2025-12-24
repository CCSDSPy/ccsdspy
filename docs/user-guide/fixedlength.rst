.. _fixed:

********************
Fixed Length Packets
********************

Overview
========
Fixed length packets are one type of packet defined in the CCSDS packet standard.
This kind of packet does not change in length and so is the easiest to parse quickly since the start of the next packet can easily be calculated.
This packet type is in contrast to variable length packets which are also supported (see `ccsdspy.VariableLength`).

.. contents::
   :depth: 2

Defining a packet
=================
Fixed length packets are ones that only include `~ccsdspy.PacketField` that do not vary in size.
The only `~cccsds.PacketField` which has the option to be variable is `~ccsdspy.PacketArray`.
The following code defines a simple fixed length packet

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField, PacketArray

   pkt = ccsdspy.FixedLength([
        PacketField(name='SHCOARSE', data_type='uint', bit_length=32),
        PacketField(name='SHFINE',   data_type='uint', bit_length=20),
        PacketField(name='OPMODE',   data_type='uint', bit_length=3),
        PacketField(name='SPACER',   data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE',  data_type='int',  bit_length=8)
   ])

Note that the CCSDS header need not be included as it is included by default.

Alternatively, fixed length packets can be :ref:`loaded from a CSV file <loadfile>`.

Parsing a file
==============
Once a `~ccsdspy.FixedLength` object is defined, it can be used to read a binary file containing those packets.

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField, PacketArray

   pkt = ccsdspy.FixedLength([
        PacketField(name='SHCOARSE', data_type='uint', bit_length=32),
        PacketField(name='SHFINE',   data_type='uint', bit_length=20),
        PacketField(name='OPMODE',   data_type='uint', bit_length=3),
        PacketField(name='SPACER',   data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE',  data_type='int',  bit_length=8),
	PacketArray(
            name='SENSOR_GRID',
            data_type='uint',
            bit_length=16,
            array_shape=(32, 32),
            array_order='C'
	),
   ])

   result = pkt.load('MyCCSDS.tlm')

The result is returned as a dictionary, containing the names as keys and values are each a `~numpy.ndarray` of the interpreted data from each packet.
The bit length of the `~numpy.ndarray` elements will be rounded up to the next nearest byte.

When parsing fixed-length packets, the library performs the following checks:

- **Packet Definition Length Check**: Ensures the total bit length of the defined fields matches the packet length from the primary header. If all fields lack explicit `bit_offset`, an `AssertionError` is raised if they mismatch (note: this may be disabled in optimized runs). If the definition exceeds the packet length, a `RuntimeError` is raised with details on the bit discrepancy.
- **Header Checks**: Automatically checks the CCSDS header fields for consistency. See :ref:`inspecting_headers`.


.. _inspecting_headers:

Inspecting the CCSDS Headers
============================

When loading both fixed and variable length packets, the library checks the primary header fields in all packets to ensure they are consistent.
The library automatically performs the following checks:

- **Multiple APIDs**: Issues a `UserWarning` if more than one APID is detected, e.g., "Found multiple AP IDs {list}".
- **Sequence Count Order**: Issues a `UserWarning` if sequence counts are out of order, e.g., "Sequence count are out of order."
- **Missing Packets**: Issues a `UserWarning` if sequence counts have gaps, e.g., "Missing packets found {list}".

.. _getting-header:

Getting the CCSDS Header
========================

It is also possible to return the contents of the packet primary header.
This may be important to determine the APID or check for packet loss by checking the packet sequence number.
For a definition of the CCSDS primary header see :ref:`ccsds_standard`.

.. code-block:: python

    result = pkt.load('MyCCSDS.tlm', include_primary_header=True)

This adds the following fields to the result `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`, `CCSDS_SECONDARY_FLAG`, `CCSDS_SEQUENCE_FLAG`, `CCSDS_SEQUENCE_COUNT`, `CCSDS_PACKET_LENGTH`.
