
CCSDSPy
=======

.. image:: https://github.com/ccsdspy/ccsdspy/actions/workflows/ccsdspy-ci.yml/badge.svg
    :target: https://github.com/ccsdspy/ccsdspy/actions
    :alt: CI Status

.. image:: https://img.shields.io/pypi/pyversions/ccsdspy.svg
    :target: https://pypi.org/project/ccsdspy/

.. image:: https://codecov.io/gh/ccsdspy/ccsdspy/branch/main/graph/badge.svg?token=Ia45f4cW8f
    :target: https://codecov.io/gh/ccsdspy/ccsdspy
    :alt: Code Coverage

CCSDSPy provides an IO Interface for reading CCSDS_ data in Python.
The CCSDS format is used for many NASA and ESA missions for low-level telemetry, and often contains tightly packed bits to reduce downlink requirements. The library is developed with requirements sourced from the community and extensive automated testing. 

.. _CCSDS: https://public.ccsds.org/default.aspx

.. toctree::
   :maxdepth: 2

   whatsnew/index
   user-guide/index
   dev-guide/index
   api

Used By
-------
.. image:: _static/used-by/small/goes-r.png
    :target: https://www.goes-r.gov/
.. image:: _static/used-by/small/hermes.png
    :target: https://science.nasa.gov/missions/hermes
.. image:: _static/used-by/small/punch.png
    :target: https://punch.space.swri.edu/
.. image:: _static/used-by/small/mms.jpg
    :target: https://mms.gsfc.nasa.gov/

Do you know of other missions that use CCSDSPy? Let us know `through a github issue`_!

.. _through a github issue: https://github.com/ccsdspy/ccsdspy/issues/new

Install ccsdspy
---------------
To install ccsdspy from source, you can use

.. code::

   pip install ccsdspy


Brief Tour
----------
Fixed length packets are one type of packet defined in the CCSDS packet standard.
This kind of packet has packets that does not change in length.
When provided with a description of the layout of the packet data (not including the primary CCSDS header), `ccsdspy.FixedLength` will decode the fields automatically using highly efficient vectorized shifting and masking.

The result is a dictionary, containing `ccsdspy.PacketField` names as keys.
The dictionary values are arrays containing the parsed packet data.
A simple example is shown below.

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
