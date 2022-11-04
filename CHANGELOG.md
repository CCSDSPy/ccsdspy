# Changelog

Notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
	
## [0.0.12] - 2022-08-06

  - Add split_by_apid() function and command line interface `python -m ccsdspy split`.

## [0.0.9] - 2018-11-19

### Changed

 - Improve handling of packet definitions with intermittently specified bit_offset (ie. some bit_offset specified, others None).
 - Respect byte_ordering for float datatypes.

## [0.0.8] - 2018-10-11
### Changed
- Removed astropy dependency. Changes return type of ccsdspy.FixedLength.load from astropy.table.Table to OrderedDict. 

### Added 
- CHANGELOG.
