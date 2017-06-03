
ccsdspy
=======

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
Fixed length packets are one type of packet defined in CCSDS. When provided with a description of data layout, `ccsdspy.FixedLength` will decode the fields automatically using highly efficient vectorized shifting and masking.

The result is returned as an `astropy.table.Table`.

.. code-block:: python
                
   import ccsdspy
   from ccsdspy import PacketField
   
   pkt = ccsdspy.FixedLength([
        PacketField(name='SHCOARSE',       data_type='uint', bit_length=32),
        PacketField(name='SHFINE',         data_type='uint', bit_length=20),
        PacketField(name='OPMODE',         data_type='uint', bit_length=3),
        PacketField(name='SPACER',         data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE_SENSOR', data_type='int',  bit_length=8),
   ])
   
   table = pkt.load('MyCCSDS.bin')


User Documentation
------------------
.. toctree::
  :maxdepth: 1
             
  ccsdspy/index.rst
