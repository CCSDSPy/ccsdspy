
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

It is also possible to return the contents of the CCSDS primary header. For a definition of the CCSDS primary header see :ref:`CCSDS Standard`.

.. code-block:: python

    result = pkt.load('MyCCSDS.bin', include_primary_header=True)

User Documentation
------------------
.. toctree::
  :maxdepth: 1
             
  ccsdspy.rst
