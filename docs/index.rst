
CCSDSPy
=======

.. image:: https://github.com/ddasilva/ccsdspy/actions/workflows/ccsdspy-ci.yml/badge.svg
    :target: https://github.com/ddasilva/ccsdspy/actions
    :alt: CI Status

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


Fixed Length Packets
--------------------
Fixed length packets are one type of packet defined in the CCSDS packet standard. This kind of packet has packet data that does not change in length. 
When provided with a description of the layout of the packet data (not including the primary CCSDS header), `ccsdspy.FixedLength` will decode the fields automatically using highly efficient vectorized shifting and masking.

The result is returned as a dictionary, containing PacketField names as keys and values are each array of the interpreted data from each packet.

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

It is also possible to return the contents of the CCSDS primary header. For a definition of the CCSDS primary header see :ref:`CCSDS Standard`.

.. code-block:: python

    result = pkt.load('MyCCSDS.bin', include_primary_header=True)

Splitting Mixed Streams by APID
-------------------------------
Often, CCSDS data will arrive from external sources into software systems in a single file with multiple APIDs. Splitting a mixed file or stream of bytes by APID so they can be used with the `ccsdspy.FixedLength` class can be done through the API or with the module command line interface.

.. code-block:: python

  from ccsdspy.utils import split_by_apid

  with open('mixed_file.tlm', 'rb') as mixed_file):
      # dictionary mapping integer apid to BytesIO
      stream_by_apid = split_by_apid(mixed_file)

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


User Documentation
------------------
.. toctree::
  :maxdepth: 1
             
  ccsdspy.rst
  ccsds.rst
