Notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__.

Version 1.4.1 - 2025-03-14
============================
  * Updates the `ccsdspy.utils.validate()` function so that packets are split by APID before primary headers data is parsed. This change allows for more accurate validation of the primary headers and APIDs.
  * This removes potentially misleading warnings from `read_primary_headers` for having multiple apids, having missing or out of order sequence counts.

Version 1.4.0 - 2025-03-05
============================
  * Enhanced Docstrings to call out `Raises` and `Warns` 
  * Updated sphinx docs to include descriptions of file and packet checks when loading files. 
  * Introduced new `utils.validate()` function for high-level validation of CCSDS packet files:
    
    * Checks file integrity (e.g., truncation or extra bytes) and header consistency.
    * Returns a list of warnings or exceptions (e.g., "UserWarning: File appears truncated" or "UserWarning: Found unknown APID") encountered during validation.
      
  * Supports optional `valid_apids` parameter to warn about unexpected APIDs.

Version 1.3.3 - 2025-01-31
============================
  * Fix bug where `converters.PolyConverter` and `converters.LinearConverter` would raise an exception when the field array was unsigned and coefficient was negative (`Issue #132 <https://github.com/CCSDSPy/ccsdspy/issues/132>`_)

Version 1.3.2 - 2024-10-17
============================
  * Add support for NumPy >2.0, while maintining support for <2.0
  * Fix link to bluebook and update sequence control field

Version 1.3.1 - 2024-07-30
============================
  * Pin NumPy under 2.0 to Dependencies (Support for NumPy 2 will come at a later date)

Version 1.3.0 - 2024-05-24
============================
  * Added support for custom byte orderings in  `ccsdspy.PacketField` and `ccsdspy.PacketArray`. You can now pass strings like `byte_order="3412"` in addition to `byte_order="big"` and `byte_order="little"`. (Discussion `#110 <https://github.com/CCSDSPy/ccsdspy/discussions/110>`_)

  * Implement loading variable length packets from CSV (`Issue #115 <https://github.com/CCSDSPy/ccsdspy/issues/115>`_)
  * Add documentation page: :doc:`/user-guide/loadfile`
  * Accept CCSDS header fields as converter inputs (`PR #118 <https://github.com/CCSDSPy/ccsdspy/pull/118>`_)
  * Add support `pkt.load(fh, reset_file_obj=True)` keyword argument which resets file handle to original position before loading (`Issue #111 <https://github.com/CCSDSPy/ccsdspy/issues/111>`_)
    
Version 1.2.1 - 2023-11-26
==========================
  * Fixed bug/regression introduced in 1.2.0 from signed integer patch (Discussion `#101 <https://github.com/CCSDSPy/ccsdspy/discussions/101>`_)
  * Fixed bug with expanding fields that occur in the middle of the packet (Discussion `#102 <https://github.com/CCSDSPy/ccsdspy/discussions/102>`_)

Version 1.2.0 - 2023-09-27
==========================
  * Add new class `~ccsdspy.converters.StringifyBytesConverter`, which can be used to inspect individual bytes in string representations such as binary, hexadecimal, or octal. For an introduction to post-processing transformations, see the documentation at :doc:`/user-guide/converters`.
  * Fixed issue with parsing signed integers that are not aligned to byte boundaries (Issues `#80 <https://github.com/CCSDSPy/ccsdspy/issues/80>`_ and `#76 <https://github.com/CCSDSPy/ccsdspy/issues/76>`_)
  * Corrected several spelling errors and typos in the documentation.

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
