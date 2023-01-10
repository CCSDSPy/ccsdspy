.. _utils:

*********
Utilities
*********

Overview
========
This package provides a number of utilities to work with CCSDS packets.

Splitting Mixed Streams by APID
-------------------------------
Often, CCSDS data will arrive from external sources into software systems in a single file with multiple APIDs.
Splitting a mixed file or stream of bytes by APID so they can be used with the `ccsdspy.FixedLength` class can be done through the API or with the module command line interface.

.. code-block:: python

  from ccsdspy.utils import split_by_apid

  with open('mixed_file.bin', 'rb') as mixed_file):
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
