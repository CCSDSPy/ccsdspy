CCSDSPy - IO Interface for Reading CCSDS Data in Python.
========================================================

.. image:: https://github.com/ccsdspy/ccsdspy/actions/workflows/ccsdspy-ci.yml/badge.svg
    :target: https://github.com/ccsdspy/ccsdspy/actions
    :alt: CI Status


.. image:: https://codecov.io/gh/ccsdspy/ccsdspy/branch/main/graph/badge.svg?token=Ia45f4cW8f
    :target: https://codecov.io/gh/ccsdspy/ccsdspy
    :alt: Code Coverage	  
    

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7819991.svg
    :target: https://doi.org/10.5281/zenodo.7819991
    :alt: Zenodo DOI
	  
This community-developed package provides a Python interface for reading tightly packed bits in the `Consultative Committee for Space Data Systems (CCSDS) <https://public.ccsds.org/default.aspx>`__ format used by many NASA and ESA missions. The library is developed with requirements sourced from the community and extensive automated testing.

Used By
-------
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/goes-r.png
    :target: https://www.goes-r.gov/
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/hermes.png
    :target: https://science.nasa.gov/missions/hermes
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/punch.png
    :target: https://punch.space.swri.edu/
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/mms.jpg
    :target: https://mms.gsfc.nasa.gov/
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/spherex.png
    :target: https://www.jpl.nasa.gov/missions/spherex
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/elfin.jpg
    :target: https://elfin.igpp.ucla.edu/
.. image:: https://raw.githubusercontent.com/ccsdspy/ccsdspy/main/docs/_static/used-by/small/padre.png
    :target: https://padre.ssl.berkeley.edu

Do you know of other missions that use CCSDSPy? Let us know `through a github issue`_!

.. _through a github issue: https://github.com/ccsdspy/ccsdspy/issues/new

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
For more information or to ask questions about the library or CCSDS data in general, check out the `CCSDSPy Discussion Board <https://github.com/ccsdspy/ccsdspy/discussions>`__ hosted through GitHub.

Acknowledging or Citing ccsdspy
===============================
If you use ccsdspy, it would be appreciated if you let us know and mention it in your publications. The code can be cited using the `DOI provided by Zenodo <https://zenodo.org/record/7819991>`__. The continued growth and development of this package is dependent on the community being aware of it.

Code of Conduct
===============
When interacting with this package please behave consistent with the following `Code of Conduct <https://www.contributor-covenant.org/version/2/1/code_of_conduct/>`__.
