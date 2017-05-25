CCSDSPy - IO Interface for Reading CCSDS Data in Python.
========================================================

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

.. image:: https://api.travis-ci.org/ddasilva/ccsdspy.svg?branch=master
    :target: https://travis-ci.org/ddasilva/ccsdspy
    :alt: Travis Status
          
This package provides a Python interface for reading tightly packed bits in the CCSDS format used for many NASA and ESA missions.

QuickStart - Decoding Fixed Length Packets
------------------------------------------
This example presents defining an APID format and decoding a file containing packets of this APID.

   >>> from spacepy import pyccsds
   >>> from spacepy.pyccsds import PacketField
   >>> 
   >>> pkt = pyccsds.FixedLength([
        PacketField(name='SHCOARSE',          data_type='uint', bit_length=32),
        PacketField(name='SHFINE',            data_type='uint', bit_length=20),
        PacketField(name='OPMODE',            data_type='int',  bit_length=3),
        PacketField(name='SPACER',            data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE_SENSOR',    data_type='int',  bit_length=8),
   ])
   >>> table = pkt.load('MyCCSDS.bin')
   >>> table['VOLTAGE_SENSOR']
       <Column name='VOLTAGE_SENSOR' dtype='uint16' length=17280>
          26540
          25929
          26905
          26408
          26388
          26923
          26475
          26425
            ...
          26799
          26792
          27190
          26286
          26989
          26577
          26459
          26826
   
Supported Data Types
--------------------
The following data types will be supported:

* uint
* int
* float
* fill
* string
 
Licensed
--------
This project is Copyright (c) Daniel da Silva and licensed under the terms of the Apache Software Licence 2.0 license. See the licenses folder for more information.
