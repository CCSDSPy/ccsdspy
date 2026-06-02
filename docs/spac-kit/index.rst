.. _spac-kit:

********
SPaC-Kit
********

**SPaC-Kit** is a collection of Python tools for working with **CCSDS Space Packets**.

Overview
========

SPaC-Kit provides command-line tools and Python APIs to:

- **Parse** CCSDS data files into Pandas DataFrames or Excel spreadsheets
- **Generate** CCSDS packets with random or zero-initialized fields for testing
- **Document** packet definitions automatically using a Sphinx extension

SPaC-Kit supports mission or instrument-specific CCSDS packet structures via **plugin** packages built on the CCSDSPy library.

.. note::

   This library is currently in active development. Some functions are placeholders and may not yet have full implementations.

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

.. code-block:: bash

   spac-parse --file downlink.bin

Generate Test Packets
---------------------

.. code-block:: bash

   spac-generate --output test.bin --apid 100 200

Auto-Generate Documentation
---------------------------

Add to your Sphinx ``conf.py``:

.. code-block:: python

   extensions = ['spac_kit.autodocs']
   spacdocs_packet_modules = ['ccsds.packets.your_mission']

Contents
========

.. toctree::
   :maxdepth: 2

   installation
   parser
   generator
   autodocs
   plugins
