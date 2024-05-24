.. _variable:

***********************
Variable Length Packets
***********************


Overview
========
A CCSDS packet may sometimes contain fields which differ in length packet-to-packet.  Parsing such variable length packets is supported through the `~ccsdspy.VariableLength`. 

Variable length fields are defined using the `~ccsdspy.PacketArray` class. There are two ways to define the length on a per-packet basis:

#. **Reference-based Variable Length Field**

   This is done by creating a `~ccsdspy.PacketArray` with `array_shape="other_field"`. In this case, `other_field` is the name of another field in the packet that sets the number of elements in the array.
  
#. **Expanding Variable Length Field**

   This is done by creating a `~ccsdspy.PacketArray` with `array_shape="expand"`. In this case, the field will grow to fill the rest of the packet, using the packet length defined in the packet header to determine how much space is left.


Please note the efficiency of parsing variable length packets is significantly decreased compared to fixed length packets.
Parsing the packets is done in the same way as `~ccsdspy.FixedLength`::

    result = pkt.load('MyCCSDS.bin')

The result will be a dictionary with the names as the keys.
The values are arrays with the `~ccsdspy.PacketArray` field providing arrays with variable sizes.
It is also possible to get access to the packet primary header. See :ref:`getting-header`.

.. warning::
    `bit_offset` cannot be specified for variable length packets. Instead, the packet definition must define all packets, and the bit offsets are calculated automatically.

.. contents::
   :depth: 2

Reference-based Variable Length Field
=====================================
An example of using a reference-based variable length field called `data1` which gets the number of elements from another field called `data1_len` is below, and similar for `data2` and `data2_len`. There is not a limit to the number of reference-based variable length fields in a packet definition. 

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField, PacketArray

    pkt = ccsdspy.VariableLength([
         PacketField(
              name='SHCOARSE',
              data_type='uint',
              bit_length=32
         ),
         PacketField(
              name='data1_len',
              data_type='uint',
              bit_length=8,
         ),	 
         PacketArray(
              name="data1",
              data_type="uint",
              bit_length=16,
              array_shape="data1_len",  # links data1 <-> data1_len
         ),
         PacketField(
              name='data2_len',
              data_type='uint',
              bit_length=8,
         ),	 
         PacketArray(
              name="data2",
              data_type="uint",
              bit_length=16,
              array_shape="data2_len",  # links data2 <-> data2_len
         ),	 
         PacketField(
              name="checksum",
              data_type="uint",
              bit_length=16
         ),
    ])
    
    result = pkt.load('MyCCSDS.tlm')


Expanding Variable Length Field
===============================
An example of using a expanding variable length field called `data` below. Because the expanding field grows to fill all remaining space, there can only be one per packet definition. 

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField, PacketArray

    pkt = ccsdspy.VariableLength([
         PacketField(
              name='SHCOARSE',
              data_type='uint',
              bit_length=32
         ),
         PacketArray(
              name="data",
              data_type="uint",
              bit_length=16,
              array_shape="expand",   # makes the data field expand
         ),
         PacketField(
              name="checksum",
              data_type="uint",
              bit_length=16
         ),
    ])
    
    result = pkt.load('MyCCSDS.tlm')
