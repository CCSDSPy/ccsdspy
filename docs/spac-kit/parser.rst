.. _spac-kit-parser:

**************
Parsing Packets
**************

The ``spac-parse`` command converts CCSDS binary data files into Excel spreadsheets with separate sheets for each packet type.

Basic Usage
===========

.. code-block:: bash

   spac-parse --file downlink.bin

This creates ``downlink.xlsx`` with one sheet per APID found in the file.

Command-Line Options
====================

**Required:**

``--file FILE``
   Path to the CCSDS binary file

**Optional:**

``--bdsem``
   Handle BDSEM-specific packet wrappers

``--pkt-header``
   Strip non-CCSDS headers between packets

``--json-header``
   Skip JSON header at file start

``--calculate-crc``
   Validate CRC and include both packet and calculated CRC in output

Examples
========

**Parse with CRC validation:**

.. code-block:: bash

   spac-parse --file downlink.bin --calculate-crc

**Handle non-CCSDS headers:**

.. code-block:: bash

   spac-parse --file downlink.bin --pkt-header

Output Format
=============

The Excel file contains:

- One sheet per APID (packet type)
- Column headers matching field names
- Each row representing one packet

Example::

   Sheet: "SensorPacket" (APID 100)
   ┌───────┬──────────┬─────────────┬────────┐
   │ Index │ SHCOARSE │ TEMPERATURE │ STATUS │
   ├───────┼──────────┼─────────────┼────────┤
   │   0   │ 12345678 │    23.45    │   1    │
   │   1   │ 12345679 │    23.46    │   1    │
   └───────┴──────────┴─────────────┴────────┘

Python API
==========

**Parse to DataFrames:**

.. code-block:: python

   from spac_kit.parser.parse_ccsds_downlink import parse_ccsds_file

   with open("downlink.bin", "rb") as f:
       dfs = parse_ccsds_file(f, do_calculate_crc=False)

   # dfs is a nested dict: {apid: {packet_name: DataFrame}}
   for apid, packet_data in dfs.items():
       for packet_name, df in packet_data.items():
           print(f"{packet_name} (APID {apid}): {len(df)} packets")

**Parse to Excel:**

.. code-block:: python

   from spac_kit.parser.downlink_to_excel import export_ccsds_to_excel

   export_ccsds_to_excel("downlink.bin", "output.xlsx", do_calculate_crc=True)

**Handle non-CCSDS headers:**

.. code-block:: python

   from spac_kit.parser.remove_non_ccsds_headers import strip_non_ccsds_headers
   from spac_kit.parser.parse_ccsds_downlink import parse_ccsds_file

   with open("data.bin", "rb") as f:
       clean_file = strip_non_ccsds_headers(f, pkt_header=True)
       dfs = parse_ccsds_file(clean_file)

Troubleshooting
===============

**No packet definitions found**

Ensure you have a plugin installed:

.. code-block:: bash

   spac-ls  # Check available packets
   pip install spac-kit-europa-clipper  # Install if needed

**Unknown APID**

Packets with unknown APIDs are skipped. Use ``spac-ls`` to see supported APIDs.
