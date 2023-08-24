.. _ccsds_standard:

*****
CCSDS
*****

Overview
========
The `Consultative Committee for Space Data Systems (CCSDS) <https://public.ccsds.org/default.aspx>`__ is a multi-national forum for the development of communications & data systems standards for spaceflight.
It maintains space communications & data handling `standards <https://public.ccsds.org/Publications/default.aspx>`__ to enhance interoperability across governmental & commercial projects.
One of the standards published by this group is the `CCSDS Space Packet protocol <https://public.ccsds.org/Pubs/133x0b2e1.pdf>`__ which defines how space missions transfer space application data both sending and receiving.
The maximum length of a CCSDS packet is 65536 octets.

A CCSDS packet is made of three parts: a required primary header, an optional secondary header, and a User data section.
The packet data consists of all parts that are not the required primary header inclusive of the optional secondary header.

.. list-table:: Space Packet Definition
   :widths: 15 10 30
   :header-rows: 1

   * - Name
     - bit length
     - Description
   * - Packet Primary Header
     - 48
     - The required CCSDS header
   * - Packet Secondary Header
     - variable
     - The optional secondary header
   * - User Data Field
     - variable
     - The data component of the packet.

Definitions
-----------
* **application process identifier, APID** - A unique identifier for a stream of packets to indicate source, destination, or type.
* **packet primary header** - The first 48 bits of every CCSDS packet (or 6 octets).
* **packet data field** - The contents of the packet not including the packet primary header. It does include the optional secondary header.
* **secondary header** - An optional second header which directly follows the primary header. It usually includes a time code. The primary header contains a field which indicates whether a secondary header is present.
* **octet** - An eight-bit word.

CCSDS Header Standard
---------------------

The mandatory packet primary header consists of four fields contained within 6 octets (each octet is 8 bits) or 48 bits.

.. list-table:: Packet Primary Header Definition
   :widths: 15 10 30
   :header-rows: 1

   * - Name
     - bit length
     - Description
   * - Packet version number
     - 3
     - The CCSDS version number. Shall be set to '000'.
   * - Packet identification field
     -
     -
   * - Packet type
     - 1
     - For telemetry (or reporting), set to '0', for a command (or request), set to '1'
   * - Secondary header flag
     - 1
     - indicates the presence or absence of a secondary header. Set to '1' if present.
   * - Application process identifier or APID
     - 11
     - The APID provides a way to uniquely identify sending or receiving applications on a space vehicle.
   * - Packet sequence control field
     -
     -
   * - Sequence flag
     - 2
     - Set to '01' if the data is a continuation segment, set to '00' if it contains the first or only segment of data.
   * - Packet sequence count or packet name
     - 14
     - the sequential binary count of each packet for a specific APID. The purpose is to allow packets to be ordered.
   * - Packet data length
     - 16
     - The length in octets of the remainder of the packet minus 1 octet.

For more information see Section 4.1.3 of the `CCSDS Blue book <https://public.ccsds.org/Pubs/133x0b2e1.pdf>`_.
