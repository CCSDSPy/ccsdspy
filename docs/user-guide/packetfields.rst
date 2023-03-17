.. _fields:

**********************
Defining Packet Fields
**********************

All fields in a packet including those in the packet primary header are defined by a name, bit length (if available), and data type.
This is done by using one of the following objects `~ccsdspy.PacketField` and `~ccsdspy.PacketArray`.
These objects are used by the packet objects `~ccsdspy.FixedLength` and `~ccsdspy.VariableLength`.

.. contents::
   :depth: 2


PacketField
===========
The `~ccsdspy.PacketField` is used to define most fields in a packet as well as the packet primary header.
It can be defined simply, for example::

    PacketField(name='SHCOARSE', data_type='uint', bit_length=32)

It requires a name, data type, as well as bit length.
The name can be any string.
This string is used as the index in the resulting dictionary once a packet is parsed.
It is also possible to provide a bit offset to define precisely its position within the packet.
This is typically not necessary because packet are defined in a list.
Without a bit offset, its value is calculated automatically assuming that the order of packet fields is correct.

PacketArray
===========
The `~ccsdspy.PacketArray` provides a simple way to define multiple repeating packet fields.
It is defined similarly to `~ccsdspy.PacketField` but adds a few new keywords, for example::

    PacketArray(name='SENSOR_GRID', data_type='uint', bit_length=16,
                array_shape=(32, 32), array_order='C')

The bit length is the value for each element in the array.
Defining it this way makes it a fixed length field.
It is also possible to use it to define a field that can have a variable size.::

    PacketArray(name="data", data_type="uint", bit_length=16,
                array_shape="expand")

This enables the parsing of variable length packets using the `~ccsdspy.VariableLength`.
