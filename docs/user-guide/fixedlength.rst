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
A packet need not be defined in code.
It can also be defined in a text file.
For example,

With this file, it is then possible to define the packet object with

.. code-block:: python

   import ccsdspy
   pkt = ccsdspy.FixedLength.from_file('packet_definition.csv')

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

.. _getting-header:

Getting the CCSDS Header
========================

It is also possible to return the contents of the packet primary header.
This may be important to determine the APID or check for packet loss by checking the packet sequence number.
For a definition of the CCSDS primary header see :ref:`ccsds_standard`.

.. code-block:: python

    result = pkt.load('MyCCSDS.tlm', include_primary_header=True)

This adds the following fields to the result `CCSDS_VERSION_NUMBER`, `CCSDS_PACKET_TYPE`, `CCSDS_SECONDARY_FLAG`, `CCSDS_SEQUENCE_FLAG`, `CCSDS_SEQUENCE_COUNT`, `CCSDS_PACKET_LENGTH`.
