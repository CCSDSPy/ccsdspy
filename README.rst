CCSDSPy - IO Interface for Reading CCSDS Data in Python.
========================================================

.. image:: https://github.com/ddasilva/ccsdspy/actions/workflows/ccsdspy-ci.yml/badge.svg
    :target: https://github.com/ddasilva/ccsdspy/actions
    :alt: CI Status


.. image:: https://codecov.io/gh/ddasilva/ccsdspy/branch/main/graph/badge.svg?token=Ia45f4cW8f
    :target: https://codecov.io/gh/ddasilva/ccsdspy
    :alt: Code Coverage	  
	  
This package provides a Python interface for reading tightly packed bits in the `Consultative Committee for Space Data Systems (CCSDS) <https://public.ccsds.org/default.aspx>`__ format used by many NASA and ESA missions.
 
Installation
============
To install ccsdspy

.. code::

   pip install ccsdspy

Usage Example
=============
The following example shows how simple it is to read in fixed length CCSDS packets.

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
   
   result = pkt.load('mypackets.bin')

Documentation
=============
Our documentation is hosted on readthedocs and can be found `here <https://ccsdspy.readthedocs.io/en/latest/>`__.

Getting Help
============
For more information or to ask questions about the library or CCSDS data in general, check out the `CCSDSPy Discussion Board <https://github.com/ddasilva/ccsdspy/discussions>`__ hosted through GitHub.

Acknowledging or Citing ccsdspy
===============================
If you use ccsdspy, it would be appreciated if you let us know and mention it in your publications. The continued growth and development of this package is dependent on the community being aware of it.

Code of Conduct
===============
When interacting with this package please behave consistent with the following `Code of Conduct <https://www.contributor-covenant.org/version/2/1/code_of_conduct/>`__.
