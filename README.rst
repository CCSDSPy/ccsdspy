CCSDSPy - IO Interface for Reading CCSDS Data in Python.
========================================================

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

.. image:: https://api.travis-ci.org/ddasilva/ccsdspy.svg?branch=master
    :target: https://travis-ci.org/ddasilva/ccsdspy
    :alt: Travis Status
          
This package provides a Python interface for reading tightly packed bits in the CCSDS format used for many NASA and ESA missions.

QuickStart
----------
This example presents defining an APID format and decoding a file containing packets of this APID.

   >>> from spacepy import pyccsds
   >>> from spacepy.pyccsds import PacketField
   >>> 
   >>> pkt = pyccsds.PacketDefinition([
        PacketField(name='SHCOARSE',          data_type='uint', bit_length=32),
        PacketField(name='SHFINE',            data_type='uint', bit_length=20),
        PacketField(name='SHEIDVALID ',       data_type='uint', bit_length=1),
        PacketField(name='SHCIDPSIDE',        data_type='uint', bit_length=1),
        PacketField(name='SHSCNO',            data_type='uint', bit_length=2),
        PacketField(name='SHEID',             data_type='uint', bit_length=8),
        PacketField(name='IDPU_OPMODE',       data_type='uint', bit_length=3),
        PacketField(name='IDPU_RUN_OPTIONS',  data_type='uint', bit_length=4),
        PacketField(name='IDPU_LAST_OPMODE',  data_type='uint', bit_length=3),
        PacketField(name='IDPU_FAIL_CNT',     data_type='uint', bit_length=8),
        PacketField(name='IDPU_FAILCODE',     data_type='uint', bit_length=5),
        PacketField(name='SPACER',            data_type='fill', bit_length=1),
        PacketField(name='VOLTAGE_SENSOR',    data_type='int',  bit_length=8),
   ])
   >>> ccsds = pyccsds.CCSDS('MyCCSDS.pkt', pkt)
   >>> data = ccsds['IDPU_OPMODE']
   >>> times = my_time_conversion(ccsds['SHCOARSE'], ccsds['SHFINE'])
   >>> ccsds.keys()
   ['SHCOARSE', 'SHFINE', 'SHEIDVALID', 'SHCIDPSIDE', 'SHSCNO', 'SHEID', 'IDPU_OPMODE',
    'IDPU_RUN_OPTIONS', 'IDPU_LAST_OPMODE', 'IDPU_FAIL_CNT', 'IDPU_FAILCODE', 'SPACER'
    'VOLTAGE_SENSOR' ]

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

