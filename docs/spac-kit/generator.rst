.. _spac-kit-generator:

*******************
Generating Packets
*******************

The ``spac-generate`` command creates valid CCSDS packets for testing parsers, data pipelines, and ground software.

Basic Usage
===========

**Generate all packets:**

.. code-block:: bash

   spac-generate --output test.bin

**Generate specific APIDs:**

.. code-block:: bash

   spac-generate --output test.bin --apid 100 200

**Generate by module:**

.. code-block:: bash

   spac-generate --output test.bin --module europa_clipper.ecm

Command-Line Options
====================

**Required:**

``-o FILE, --output FILE``
   Output file path

**Optional:**

``-a APID [APID ...], --apid APID [APID ...]``
   Generate specific APID(s) only

``-m MODULE [MODULE ...], --module MODULE [MODULE ...]``
   Generate specific module(s). Can specify full module path (``europa_clipper.ecm``) or specific packet (``europa_clipper.ecm.fg1_low``). The ``ccsds.packets`` prefix is optional.

``-n COUNT, --count COUNT``
   Number of packets per definition (default: 1)

``-z, --zeros``
   Generate zero-initialized data instead of random

Examples
========

**Multiple packets with zeros:**

.. code-block:: bash

   spac-generate --output test.bin --apid 100 200 --count 10 --zeros

**Specific packet by module:**

.. code-block:: bash

   spac-generate --output test.bin --module europa_clipper.ecm.fg1_low

**List available packets:**

.. code-block:: bash

   spac-ls

Output Statistics
=================

The generator provides file statistics:

.. code-block:: text

   Generating packets to: test.bin
     Generated 1 packet(s) for APID 100 (SensorPacket)

   Success! Generated packets written to test.bin
     2,048 bytes, entropy: 7.98 bits/byte (99.8%), chi-squared: p=0.54 (uniform)

- **Entropy**: 0.0 (all same byte) to 8.0 (perfectly random)
- **Chi-squared p-value**: > 0.05 suggests uniform distribution

Python API
==========

**Basic generation:**

.. code-block:: python

   import ccsdspy
   from spac_kit.generator import PacketGenerator

   # Define packet structure
   fields = [
       ccsdspy.PacketField(name="status", data_type="uint", bit_length=8),
       ccsdspy.PacketField(name="temperature", data_type="float", bit_length=32),
   ]
   packet_def = ccsdspy.VariableLength(fields, apid=100, name="SensorPacket")

   # Generate packets
   generator = PacketGenerator(packet_def)
   with open("packets.bin", "wb") as f:
       generator.write_packet(f, count=5, use_random=True)

**Generate with plugin packets:**

.. code-block:: python

   from spac_kit.generator import PacketGenerator
   from spac_kit.parser.util import import_ccsds_packet_packages

   # Load all packet definitions from plugins
   packets = import_ccsds_packet_packages()

   # Generate for specific APID
   packet_info = next(p for p in packets if p["packet"].apid == 100)
   generator = PacketGenerator(packet_info["packet"])

   with open("output.bin", "wb") as f:
       generator.write_packet(f, count=10, use_random=False)  # zeros

**Test fixture example:**

.. code-block:: python

   import pytest
   from io import BytesIO
   from spac_kit.generator import PacketGenerator

   @pytest.fixture
   def test_packet_data():
       """Generate test CCSDS packets."""
       buf = BytesIO()
       generator = PacketGenerator(my_packet_def)
       generator.write_packet(buf, count=5, use_random=False)
       return buf.getvalue()
