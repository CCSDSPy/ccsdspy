.. _loadfile:

******************************************
Loading Packet Definitions from a CSV File
******************************************

Overview
=========

:ref:`fixed` can be loaded from a CSV (comma separated value) file.
This is an alternative method for defining packet layouts which may be desirable to some users,
and is currently undergoing development. The syntax for loading a `~ccsdspy.FixedLength` packet from a CSV file is:

.. code-block:: python

   import ccsdspy
   pkt = ccsdspy.FixedLength.from_file('packet_definition.csv')

The syntax is the same for `~ccdspy.VariableLength` packets:

.. code-block:: python

   import ccsdspy
   pkt = ccsdspy.VariableLength.from_file('packet_definition.csv')

The only requirement is that the CSV is structured as either the :ref:`threecolumn`
or :ref:`fourcolumn`.

.. contents::
   :depth: 2

.. _threecolumn:

Basic Layout (Three Columns)
============================

The basic CSV layout has columns for `name`, `data_type`, and `bit_length`. The first row of the CSV should be a
header line where the columns are named. Subsequent rows encode packet fields. This format is appropriate if the CSV
defines all the packets one after another without skipping any. The three column format automatically
calculates the bit offsets assuming that the packet order is correct. See the :ref:`fourcolumn` format
for more flexibility.

.. csv-table:: Basic Layout CSV
   :file: ../../ccsdspy/tests/data/packet_def/basic_csv_3col.csv
   :widths: 30, 30, 30
   :header-rows: 1

When the example above is loaded, five `~ccsdspy.PacketField` objects are defined
with varying names, data types, and bit lengths. To create a `~ccsdspy.PacketArray` instead, define the data type with
both the type and array shape.

.. csv-table:: Basic Layout CSV with `~ccsdspy.PacketArray`
   :file: ../../ccsdspy/tests/data/packet_def/basic_csv_3col_with_array.csv
   :widths: 30, 30, 30
   :header-rows: 1

In the example above, `VOLTAGE` would instead be a `~ccsdspy.PacketArray` of type `int` with shape `(12, 24)`.

For :ref:`variable`, the array shape string can be specified either as `expand` or as the name of another field.

.. csv-table:: Basic Layout CSV with `~ccsdspy.PacketArray` for Variable Length Packets
   :file: ../../ccsdspy/tests/data/packet_def/basic_csv_3col_with_all.csv
   :widths: 30, 30, 30
   :header-rows: 1

.. _fourcolumn:

Extended Layout (Four Columns)
==============================

The extended CSV layout has columns for `name`, `data_type`, `bit_length`, and `bit_offset`.
The first row of the CSV should be a header line where the columns are named. Subsequent rows encode packet fields.
This format allows more flexibility than the basic layout because bit offsets are explicitly defined instead
of automatically calculated. Due to this, some packet fields can be skipped
since the bit offset indicates exactly where the packet begins.

.. csv-table:: Extended Layout CSV
   :file: ../../ccsdspy/tests/data/packet_def/extended_csv_4col.csv
   :widths: 30, 30, 30, 30
   :header-rows: 1

When the example above is loaded, five `~ccsdspy.PacketField` objects are defined
with varying names, data types, and bit lengths. To create a `~ccsdspy.PacketArray` instead, define the data type with
both the type and array shape.

.. csv-table:: Extended Layout CSV with `~ccsdspy.PacketArray`
   :file: ../../ccsdspy/tests/data/packet_def/extended_csv_4col_with_array.csv
   :widths: 30, 30, 30, 30
   :header-rows: 1

In the example above, `SHSCOARSE` would instead be a `~ccsdspy.PacketArray` of type `uint` with shape `(4)`.

.. note::
    :ref:`variable` are not supported in the extended layout since `bit_offset` cannot be specified for variable length packets.

Limitations of the CSV format
=============================

The CSV format is in development and is currently limited. The limitations are:

* the byte order cannot be defined in the CSV.
* the array order cannot be defined in the CSV.
