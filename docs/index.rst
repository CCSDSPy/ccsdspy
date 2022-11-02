
CCSDSPy
=======

.. image:: https://api.travis-ci.org/ddasilva/ccsdspy.svg?branch=master
    :target: https://travis-ci.org/ddasilva/ccsdspy
    :alt: Travis Status

.. image:: https://img.shields.io/pypi/pyversions/ccsdspy.svg
    :target: https://pypi.org/project/ccsdspy/

CCSDSPy provides an IO Interface for reading CCSDS_ data in Python. The CCSDS format is used for many NASA and ESA missions for low-level telemetry, and often contains tightly packed bits to reduce downlink requirements.

.. _CCSDS: https://public.ccsds.org/default.aspx

Install ccsdspy
---------------
To install ccsdspy from source, you can use

.. code::

   pip install ccsdspy

   
.. note:: The CCSDS space packet protocol is a not a self-describing data format.
          Context for how to interpret the file's bits must be provided. This 
          information is typically available from the flight software documentation.

CCSDS Standard
--------------
A CCSDS packet is made of three parts: a required primary header, an optional secondary header, and a User data section.
The packet data consists of all parts that are not the required primary header inclusive of the optional secondary header.
The CCSDS mandatory primary header consists of four fields contained within 6 octets (each octet is 16 bits) or 96 bits.

* **Packet version number (3 bits)** - The CCSDS version number. Shall be set to '000'.
* **Packet identification field (13 bits)**
    - **Packet type (1 bit)** - For telemetry (or reporting), set to '0', for a command (or request), set to '1'
    - **Secondary header flag (1 bit)** - identicates the presence or absence of a secondary header. Set to '1' if present.
    - **Application process identifier (11 bits)** - The APID provides a way to uniquely identify sending or receiving applications on a space vehicle.
* **Packet sequence control field (16 bits)**
    - **Sequence flag (2 bits)** - set to '01' if the data is a continuation segment, set to '00' if it contains the first segment of data.
    - **Packet sequence count or packet name** - the sequential binary count of each packet for a specific APID. The purpose is to allow packets to be ordered.
* **Packet data length (16 bits)** - provides the length in octets of the remainder of the packet minus 1 octet.

For more information see Section 4.1.3 of the `CCSDS Blue book <https://public.ccsds.org/Pubs/133x0b2e1.pdf>`_.


Fixed Length Packets
--------------------
Fixed length packets are one type of packet defined in the CCSDS packet standard. This kind of packet has packet data that does not change in length. 
When provided with a description of the layout of the packet data (not including the primary CCSDS header), `ccsdspy.FixedLength` will decode the fields automatically using highly efficient vectorized shifting and masking.

The result is returned as an OrderedDict, containing PacketField names as keys and values are each array of the interpreted data from each packet.

.. code-block:: python
                
   import ccsdspy
   from ccsdspy import PacketField
   
   pkt = ccsdspy.FixedLength([
        PacketField(name='SHCOARSE', data_type='uint', bit_length=32),
        PacketField(name='SHFINE',   data_type='uint', bit_length=20),
        PacketField(name='OPMODE',   data_type='uint', bit_length=3),
        PacketField(name='SPACER',   data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE',  data_type='int',  bit_length=8),
   ])
   
   result = pkt.load('MyCCSDS.bin')

It is also possible to return the contents of the CCSDS primary header

.. code-block:: python

    result = pkt.load('MyCCSDS.bin', include_primary_header=True)

User Documentation
------------------
.. toctree::
  :maxdepth: 1
             
  ccsdspy.rst
