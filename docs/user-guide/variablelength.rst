.. _variable:

***********************
Variable Length Packets
***********************

Overview
========
The CCSDS packet primary header contains contains a length field which can vary from packet to packet.
Parsing such variable length packets is also supported through the `~ccsdspy.VariableLength`.
A variable length packet is one containing one and only one variable length field.
This packet provides the `~ccsdspy.PacketArray` field which can be set to variable length.
An example is provided below.

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField, PacketArray, VariableLength

    pkt = VariableLength(
            [
                PacketField(name='SHCOARSE', data_type='uint', bit_length=32),
                PacketArray(
                    name="data",
                    data_type="uint",
                    bit_length=16,
                    array_shape="expand",
                ),
                PacketField(name="checksum", data_type="uint", bit_length=16),
            ]
        )

The efficiency of parsing variable length packets is significantly decreased compared to fixed length packets.
Parsing the packets is done in the same way as `~ccsdspy.FixedLength`::

    result = pkt.load('MyCCSDS.bin')

The result will be a dictionary with the names as the keys.
The values are arrays with the `~ccsdspy.PacketArray` field providing arrays with variable sizes.
It is also possible to get access to the packet primary header. See :ref:`getting-header`.
