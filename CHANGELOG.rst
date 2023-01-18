Notable changes to this project will be documented in this file.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`__.

Dev
===
  * Major new documentation added and re-organization.
  * Started tracking coverage percentage
  * Moved packaging to use [Poetry](https://python-poetry.org)

Version 0.0.13 - 2022-01-03
===========================
  * Added the ability to parse variable length files
  * Added the ability to specify packet field that are arrays
  * Added the ability to define a packet through a csv file
  * Added github actions to perform continuous intergration
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
