.. _spac-kit-plugins:

*******
Plugins
*******

SPaC-Kit uses a plugin architecture to support mission-specific CCSDS packet structures. Plugins are Python packages that define packet layouts using CCSDSPy.

Available Plugins
=================

**Europa Clipper**

.. code-block:: bash

   pip install spac-kit-europa-clipper

Repository: https://github.com/nasa-jpl/spac-kit-europa-clipper

Using Plugins
=============

List installed packet definitions:

.. code-block:: bash

   spac-ls

Example output::

   Available packet definitions:

   Module: ccsds.packets.europa_clipper.ecm
     APID 100: fg1_low - Low-rate Field Geometry 1
     APID 101: fg1_high - High-rate Field Geometry 1

   Total: 2 packet definitions from 1 module(s)

Creating a Plugin
=================

Structure
---------

.. code-block:: text

   my-mission-plugin/
   ├── src/
   │   └── ccsds/
   │       └── packets/
   │           └── my_mission/
   │               ├── __init__.py
   │               └── telemetry.py
   ├── pyproject.toml
   └── README.md

Define Packets
--------------

In ``telemetry.py``:

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField

   sensor_data = ccsdspy.FixedLength([
       PacketField(
           name='timestamp',
           data_type='uint',
           bit_length=32,
           description='Spacecraft time in seconds'
       ),
       PacketField(
           name='temperature',
           data_type='float',
           bit_length=32,
           description='Temperature in Celsius'
       ),
   ], apid=100, name="SensorData")

Best Practices
--------------

1. **Descriptive names**: Use clear field and packet names
2. **Add descriptions**: Include ``description`` parameter for all fields
3. **Document APIDs**: Comment APID assignments clearly
4. **Semantic versioning**: Use semver for your plugin releases
5. **Include tests**: Validate packet definitions parse correctly

Discovery
---------

SPaC-Kit automatically discovers any package under the ``ccsds.packets`` namespace. No configuration needed - just install and use.
