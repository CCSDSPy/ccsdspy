.. _CCSDS Standard:

CCSDS Standard
--------------
A CCSDS packet is made of three parts: a required primary header, an optional secondary header, and a User data section.
The packet data consists of all parts that are not the required primary header inclusive of the optional secondary header.
The CCSDS mandatory primary header consists of four fields contained within 6 octets (each octet is 8 bits) or 48 bits.

* **Packet version number (3 bits)** - The CCSDS version number. Shall be set to '000'.
* **Packet identification field (13 bits)**
    - **Packet type (1 bit)** - For telemetry (or reporting), set to '0', for a command (or request), set to '1'
    - **Secondary header flag (1 bit)** - identicates the presence or absence of a secondary header. Set to '1' if present.
    - **Application process identifier (11 bits)** - The APID provides a way to uniquely identify sending or receiving applications on a space vehicle.
* **Packet sequence control field (16 bits)**
    - **Sequence flag (2 bits)** - set to '01' if the data is a continuation segment, set to '00' if it contains the first segment of data.
    - **Packet sequence count or packet name (14 bits)** - the sequential binary count of each packet for a specific APID. The purpose is to allow packets to be ordered.
* **Packet data length (16 bits)** - provides the length in octets of the remainder of the packet minus 1 octet.

For more information see Section 4.1.3 of the `CCSDS Blue book <https://public.ccsds.org/Pubs/133x0b2e1.pdf>`_.
