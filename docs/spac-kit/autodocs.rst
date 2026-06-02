.. _spac-kit-autodocs:

**************************
Documentation Generation
**************************

SPaC-Kit includes a **Sphinx extension** that automatically generates comprehensive documentation for CCSDS packet definitions. This is the standout feature of SPaC-Kit, enabling missions to maintain living documentation that stays synchronized with packet definitions.

Overview
========

The ``spac_kit.autodocs`` Sphinx extension:

- **Discovers** all packet definitions from installed plugins
- **Generates** RST stub files automatically
- **Creates** formatted documentation with field tables
- **Links** field names to detailed descriptions
- **Styles** output with mission-specific CSS

This eliminates manual documentation maintenance and ensures packet specs stay current with code.

Quick Start
===========

Add to your Sphinx ``conf.py``:

.. code-block:: python

   extensions = [
       'sphinx.ext.autodoc',
       'spac_kit.autodocs',  # Add this line
   ]

   # Configure which modules to document
   spacdocs_packet_modules = [
       'ccsds.packets.europa_clipper.ecm',
       'ccsds.packets.europa_clipper.status',
   ]

Then build your docs:

.. code-block:: bash

   sphinx-build -b html docs/ docs/_build/html

The Sphinx Extension
====================

The extension provides the ``.. spacdocs::`` directive for documenting individual packets, and automatically generates a complete packet index.

Configuration
=============

In your ``conf.py``:

.. code-block:: python

   extensions = ['spac_kit.autodocs']

   # Required: List of Python module paths containing packet definitions
   spacdocs_packet_modules = [
       'ccsds.packets.your_mission.telemetry',
       'ccsds.packets.your_mission.commands',
   ]

The extension will:

1. Scan each module for ``_BasePacket`` instances
2. Generate an RST stub file for each packet
3. Create a master index file (``_packet_index.rst``)
4. Copy styling resources to your ``_static`` directory

Using the spacdocs Directive
=============================

Manual usage (the extension does this automatically):

.. code-block:: rst

   Sensor Data Packet
   ==================

   .. spacdocs:: ccsds.packets.europa_clipper.ecm.sensor_data

This generates:

- **Summary table** with all fields, types, bit lengths, and offsets
- **Detail sections** for each field with full attribute listings
- **Interactive tooltips** showing field descriptions
- **Hyperlinks** from summary to details

Generated Documentation Structure
==================================

For each packet, the extension creates:

**Summary Section**

A table showing:

- Field names (clickable, with tooltip descriptions)
- Data types (with array notation if applicable)
- Bit lengths
- Bit offsets (calculated automatically)
- Byte order

**Detail Sections**

For each field:

- Field name as section header
- Full description
- Complete attribute table (data type, bit length, offset, byte order, array shape, array order)


Advanced Features
=================

Field Descriptions
------------------

Add descriptions to your packet fields:

.. code-block:: python

   PacketField(
       name='status',
       data_type='uint',
       bit_length=8,
       description='System status flags: bit 0=power, bit 1=thermal'
   )

Descriptions appear as tooltips in the summary table and as paragraph text in detail sections.

Array Fields
------------

Array fields are automatically formatted:

.. code-block:: python

   PacketArray(
       name='sensor_grid',
       data_type='uint',
       bit_length=16,
       array_shape=(32, 32)
   )

Appears in documentation as: ``uint[32,32]``

Directory Structure
===================

After building, your docs directory contains:

.. code-block:: text

   docs/
   ├── conf.py
   ├── index.rst
   ├── _static/
   │   ├── spac-kit.css          # Auto-copied
   │   └── circle-info.svg       # Auto-copied
   ├── _autopackets/             # Auto-generated
   │   ├── packet_name1.rst
   │   ├── packet_name2.rst
   │   └── ...
   └── _packet_index.rst         # Auto-generated

Include ``_packet_index.rst`` in your main toctree:

.. code-block:: rst

   .. toctree::
      :maxdepth: 2

      introduction
      _packet_index
      api

Integration Example
===================

Complete ``conf.py`` example:

.. code-block:: python

   # Sphinx configuration

   project = 'Europa Clipper Packets'
   extensions = [
       'sphinx.ext.autodoc',
       'sphinx.ext.napoleon',
       'spac_kit.autodocs',
   ]

   # SPaC-Kit configuration
   spacdocs_packet_modules = [
       'ccsds.packets.europa_clipper.ecm',
       'ccsds.packets.europa_clipper.ice',
       'ccsds.packets.europa_clipper.mimi',
   ]

   # HTML output options
   html_theme = 'sphinx_rtd_theme'
   html_static_path = ['_static']

Main documentation file (``index.rst``):

.. code-block:: rst

   Europa Clipper Packet Documentation
   ====================================

   .. toctree::
      :maxdepth: 2

      overview
      _packet_index
      usage
