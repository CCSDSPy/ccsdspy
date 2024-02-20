.. _loadfile:

**************************************
Loading Packet Definitions from a File
**************************************

Overview
=========

:ref:`fixed` can be loaded from a CSV file:

.. code-block:: python

   import ccsdspy
   pkt = ccsdspy.FixedLength.from_file('packet_definition.csv')

The only requirement is that the CSV is structured as either the :ref:`three column <threecolumn>`
or :ref:`four column <fourcolumn>` format.

At the moment, :ref:`variable` cannot be loaded from a CSV file.

.. contents::
   :depth: 2

.. _threecolumn:

Three column CSV
===================

The three column CSV format has columns for `name`, `data_type`, and `bit_length`. The first row of the CSV should be a
header line where the columns are named. Subsequent rows encode packet fields. This format is appropriate if the CSV
defines all the packets one after another without skipping any. The three column format automatically
calculates the bit offsets assuming that the packet order is correct. See the :ref:`fourcolumn` format
for more flexibility.

.. csv-table:: Simple Three Column CSV
   :file: ../../ccsdspy/tests/data/packet_def/simple_csv_3col.csv
   :widths: 30, 30, 30
   :header-rows: 1

When the example above is loaded, five `~ccsdspy.PacketField` objects are defined
with varying names, data types, and bit lengths. To create a `~ccsdspy.PacketArray` instead, define the data type with
both the type and array shape.

.. csv-table:: Three Column CSV with `~ccsdspy.PacketArray`
   :file: ../../ccsdspy/tests/data/packet_def/simple_csv_3col_with_array.csv
   :widths: 30, 30, 30
   :header-rows: 1

In the example above, `VOLTAGE` would instead be a `~ccsdspy.PacketArray` of type `int` with shape `(12, 24)`.

.. _fourcolumn:

Four column CSV
==================

The four column CSV format has columns for `name`, `data_type`, `bit_length`, and `bit_offset`.
The first row of the CSV should be a header line where the columns are named. Subsequent rows encode packet fields.
This format allows more flexibility than the three column CSV format because bit offsets are explicitly defined instead
of automatically calculated. Due to this, some packet fields can be skipped
since the bit offset indicates exactly where the packet begins.

.. csv-table:: Simple Four Column CSV
   :file: ../../ccsdspy/tests/data/packet_def/simple_csv_4col.csv
   :widths: 30, 30, 30, 30
   :header-rows: 1

When the example above is loaded, five `~ccsdspy.PacketField` objects are defined
with varying names, data types, and bit lengths. To create a `~ccsdspy.PacketArray` instead, define the data type with
both the type and array shape.

.. csv-table:: Four Column CSV with `~ccsdspy.PacketArray`
   :file: ../../ccsdspy/tests/data/packet_def/simple_csv_4col_with_array.csv
   :widths: 30, 30, 30, 30
   :header-rows: 1

In the example above, `SHSCOARSE` would instead be a `~ccsdspy.PacketArray` of type `uint` with shape `(4)`.

Limitations of the CSV format
=============================

Not all features of `ccsdspy` are currently supported with the CSV format.

For `~ccsdspy.PacketField` the byte order cannot be defined in the CSV.

For `~ccsdspy.PacketArray` the array order and byte order cannot be defined in the CSV.

Also, :ref:`variable` cannot currently be loaded from a CSV file.
