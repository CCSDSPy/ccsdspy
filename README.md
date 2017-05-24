<<<<<<< HEAD
# IO Interface for Reading CCSDS Data in Python.

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge




## Licensed

This project is Copyright (c) Daniel da Silva and licensed under the terms of the Apache Software Licence 2.0 license. See the licenses folder for more information.
=======
# PyCCSDS
This package provides a Python interface for reading tightly packed bits in the CCSDS format used for many NASA and ESA missions. The CCSDS standard is defined by the [Consultive Committee for Space Data Systems](http://ccsds.org).

## QuickStart
This example presents defining an APID format and decoding a file containing packets of this APID.
```python
>>> from spacepy import pyccsds
>>> from spacepy.pyccsds import PacketField

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
```

## Decoding a Single Field
Decoding a single field can be more efficient. To do this, provide only the field you wish to decode in the packet definition and be sure to use a `bit_offset`. Normally, these offsets are computed automatically.

```python
>>> from spacepy import pyccsds
>>> from spacepy.pyccsds import PacketField

>>> pkt = pyccsds.PacketDefinition([
        PacketField(name='IDPU_LAST_OPMODE', data_type='uint', bit_length=3, bit_offset=119),
   ])
>>> ccsds = pyccsds.CCSDS('MyCCSDS.pkt', pkt)
>>> data = ccsds['IDPU_LAST_OPMODEE']
>>> ccsds.keys()
['IDPU_LAST_OPMODE']
```
## Supported Data Types
The following data types will be supported:
- uint
- int
- float
- fill


## Restrictions
The following restrictions will be present in the first version:
- File contains only one APID (could be mitigated with some Cython)
- Signed integers must be 8, 16, 32, or 64 bits and byte aligned (could be mitigated, haven't written the logic)
- Floats must be 32 or 64 bits and byte aligned (could a use case be justified?)
- No write support (could a use case be justified?)
>>>>>>> b42bc9f7f5df8cbd3a2490c372bdec54bf7195e2
