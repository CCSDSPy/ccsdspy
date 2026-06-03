.. _spac-kit:

********
SPaC-Kit
********

**SPaC-Kit** is a collection of Python tools for working with **CCSDS Space Packets**.
It supports mission or instrument-specific CCSDS packet structures via **plugin** packages built on the CCSDSPy library. Plugins should follow the `SPaC-Kit plugin template <https://github.com/CCSDSPy/spac-kit-plugin-template>`_.

Overview
========

SPaC-Kit provides command-line tools and Python APIs to:

- **Parse** CCSDS data files into Pandas DataFrames or Excel spreadsheets
- **Generate** CCSDS packets with random or zero-initialized fields for testing
- **Document** packet definitions automatically using a Sphinx extension

.. admonition:: Acknowledgements

   The development of this library has been initialized during the development of the Europa-Clipper Science Data System, the sample file and documentation generators feature and the packaging of the code have been specifically funded through a NASA ROSES 2024 call.

Quick Start
===========

Installation
------------

Install a plugin library first (e.g., Europa Clipper):

.. code-block:: bash

   pip install spac-kit-europa-clipper
   pip install spac-kit

Parse CCSDS Data
----------------

The CCSDS Space Packet definition found in the Europa-Clipper plugin will be used to parse the input file.

.. code-block:: bash

   spac-parse --file downlink.bin

Generate Test Packets
---------------------

See the list of packet definitions available in your environment:

.. code-block:: bash

   spac-ls

This should return something like:

.. code-block:: bash

    APID  PACKET                                                                         NAME                           DESCRIPTION
    -------------------------------------------------------------------------------------------------------------------------------
    1025  europa_clipper.radmon.metadata_radmon                                          metadata_radmon                RADMON Metadata packet structure
    1089  europa_clipper.pimsu.metadata_pimsu                                            metadata_pimsu                 PIMSU Metadata packet structure.
    ...


Select the APID of the packets you want to generate data for and the number of packets expected:

.. code-block:: bash

   spac-generate --output test.bin --apid 1025 --count 200

Auto-Generate Documentation
---------------------------

An example of generated documentation can be found for the `Europa-Clipper packets <https://nasa-jpl.github.io/spac-kit-europa-clipper/>`_.

To get the generated documentation for your CCSDS packets, add to your Sphinx ``conf.py``:

.. code-block:: python

   extensions = ['spac_kit.autodocs']
   spacdocs_packet_modules = ['ccsds.packets.your_mission']


Want to start your own CCSDS packet library for your mission or instrument ?
============================================================================

Use the documented SPac-Kit plugin `github template <https://github.com/CCSDSPy/spac-kit-plugin-template>`_.


Details
========

.. toctree::
   :maxdepth: 2

   installation
   parser
   generator
   autodocs

