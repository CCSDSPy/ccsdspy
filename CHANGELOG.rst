Notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__.

Version 1.1.0 - 2023-04-11
==========================
  * Added a `~ccsdspy.converters` system, which applies post-process to decoded packet fields. This post-processing includes applying linear/polynomial calibration curves, dictionary replacement, and time parsing. See the documentation at :doc:`/user-guide/converters`.

  * Major extensions to `~ccsdspy.VariableLength` class to support arrays whose length is determined by another field. See documentation at :doc:`/user-guide/variablelength`.
  * Added the following utility functions to the `ccsdspy.utils` module. See documentation at :doc:`/user-guide/utils`.
    
    * `~ccsdspy.utils.read_primary_headers()`
    * `~ccsdspy.utils.iter_packet_bytes()`
    * `~ccsdspy.utils.split_packet_bytes()`
    * `~ccsdspy.utils.count_packets()`
    * `~ccsdspy.utils.get_packet_apid()`
    * `~ccsdspy.utils.get_packet_total_bytes()`

  * Add warnings when issues are detected in the primary headers when loading data. Warnings are issued in the following scenarios. This information can also be found in the documentation for the `~FixedLength.load()` method.

    * `UserWarning`: The CCSDS sequence count headers are not in order
    * `UserWarning`: The CCSDS sequence count headers indicate missing packets
    * `UserWarning`: There was more than one APID present in the decoded stream
      
Version 1.0.0 - 2023-02-02
===========================
  * Major new documentation added and re-organization.
  * Started tracking coverage percentage
  * Repackaging using pyproject.toml file

Version 0.0.13 - 2023-01-03
===========================
  * Added the ability to parse variable length files
  * Added the ability to specify packet field that are arrays
  * Added the ability to define a packet through a csv file
  * Added github actions to perform continuous integration
  * Specified black as the only accepted code formatter

Version 0.0.12 - 2022-08-06
===========================

  * Add split_by_apid() function and command line interface `python -m ccsdspy split`.

Version 0.0.9 - 2018-11-19
==========================

  * Improve handling of packet definitions with intermittently specified bit_offset (ie. some bit_offset specified, others None).
  * Respect byte_ordering for float datatypes.

Version 0.0.8 - 2018-10-11
==========================

  * Removed astropy dependency. Changes return type of ccsdspy.FixedLength.load from astropy.table.Table to OrderedDict.
  * Added CHANGELOG.
