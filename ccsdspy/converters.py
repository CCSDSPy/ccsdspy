"""This class hold the implementation of the converter system, which applies 
post-process to decoded packet fields. This post-processing includes applying
linear/polynomial calibration curves, dictionary replacement, and time parsing.
"""

from datetime import datetime, timedelta

import numpy as np

__all__ = [
    "EnumConverterMissingKey",
    "Converter",
    "PolyConverter",
    "LinearConverter",
    "EnumConverter",
    "DatetimeConverter",
]


class EnumConverterMissingKey(RuntimeError):
    """During conversion a value was encountered which did not have a
    corresponding key in the replacement dictionary.
    """


class Converter:
    """Base class for all converter objects.

    This class is extended to create converters, and users may extend this
    class to write their own custom converters.

    To write a converter, one must create a subclass and override either the method
    `convert(*field_arrays)`. This method implements the conversion for an entire
    sequence of decoded packet field values in a single call.
    """

    def __init__(self):
        raise NotImplementedError("This is a base class not meant to be instantiated directly")

    def convert(self, field_array):
        """Convert a sequence of decoded packet field values.

        Parameters
        ----------
        field_array : NumPy array
            decoded packet field values, must have at least one dimension

        Returns
        -------
        converted_field_array : NumPy array
            converted form of the decoded packet field values
        """
        raise NotImplementedError("This method must be overridden by a subclass")


class PolyConverter(Converter):
    """Post-processing conversion which applies calibration using a series
    of coefficients ordered from highest power to intercept.
    """

    def __init__(self, coeffs):
        """Instantiate a PolyConverter object

        Parameters
        ----------
        coeffs : list of float
           Polynomial coefficients ordered from highest power to intercept.
        """
        self._coeffs = coeffs

    def convert(self, field_array):
        """Apply the polynomial conversion.

        Parameters
        ----------
        field_array : NumPy array
            decoded packet field values, must have at least one dimension

        Returns
        -------
        converted : NumPy array
            converted form of the decoded packet field values
        """
        converted = np.zeros(field_array.shape, dtype=np.float64)

        for power, coeff in enumerate(reversed(self._coeffs)):
            converted += coeff * field_array**power

        return converted


class LinearConverter(PolyConverter):
    """Post-processing conversion which applies a linear (y=mx+b)
    transformation.
    """

    def __init__(self, slope, intercept):
        """Instantiate a LinearConverter"""
        super().__init__([slope, intercept])


class EnumConverter(Converter):
    """Post-processing conversion for applying dictionary replacement of
    integers to strings.

    If during conversion a value is encountered which does not have a
    corresponding key in the replacement dictionary, then a
    `:py:class:`~ccsdspy.converters.EnumConverterMissingKey` exception
    will be thrown.
    """

    def __init__(self, replace_dict):
        """Initialize a EnumConverter.

        Parameters
        ----------
        replace_dict : dict of int to string
           Replacement dictionary mapping integer values to string values

        Raises
        ------
        TypeError
           Either one of the keys of the replacement dictionary is not an
           integer, or one of the values is not a string.
        """
        self._replace_dict = replace_dict

        for key, value in replace_dict.items():
            if not isinstance(key, int):
                raise TypeError(
                    f"Found key in EnumConverter replacement dictionary that is "
                    f"not an integer: {repr(key)}"
                )
            if not isinstance(value, str):
                raise TypeError(
                    f"Found value in EnumConverter replacement dictionary that is "
                    f"not a string: {repr(value)}"
                )

    def convert(self, field_array):
        """Apply the enum replacement conversion.

        Parameters
        ----------
        field_array : NumPy array
            decoded packet field values, must have at least one dimension

        Returns
        -------
        converted : NumPy array
            converted form of the decoded packet field values
        """
        converted = np.zeros(field_array.shape, dtype=object)
        converted_mask = np.zeros(field_array.shape, dtype=bool)

        for key, value in self._replace_dict.items():
            converted[field_array == key] = value
            converted_mask[field_array == key] = True

        if not converted_mask.all():
            missing_keys = field_array[~converted_mask].tolist()

            raise EnumConverterMissingKey(
                f"The following were encountered which did not have "
                f"corresponding keys in the replacment dictionary: "
                f"{repr(missing_keys)}"
            )

        return converted


class DatetimeConverter(Converter):
    """Post-processing conversion for converting timestamp fields to datetime
    instances, computed using offset(s) from a reference time.

    This class supports the offsets stored in multiple input fields, for example
    where one field is a coarse time (eg seconds) and a second field is a fine
    time (eg nanoseconds). To use multiple input fields, pass a tuple of input
    field names when this converter is added to the packet.
    """

    _VALID_UNITS = (
        "days",
        "hours",
        "minutes",
        "seconds",
        "milliseconds",
        "microseconds",
        "nanoseconds",
    )
    _MILLISECONDS_PER_SECOND = 1_000
    _MICROSECONDS_PER_SECOND = 1_000_000
    _NANOSECONDS_PER_SECOND = 1_000_000_000

    def __init__(self, since, units):
        """Initialize a DatetimeConverter

        Parameters
        ----------
        since : datetime
          Reference datetime. The time stored in the field(s) is considered an
          offset to this reference. If this has timezone information attached to
          it, so will the converted datetimes.
        units : str or tuple of str
          Units string of tuples of units strings for the offset of each
          input field.  Valid units are "days", "minutes", "milliseconds",
          "microseconds", and "nanoseconds".

        Raises
        ------
        TypeError
          One of the input arguments is not of the correct type
        ValueError
          One or more of the units are invalid
        """
        if not isinstance(since, datetime):
            raise TypeError("Argument 'since' must be an instance of datetime")

        if isinstance(units, str):
            units_tuple = (units,)
        elif isinstance(units, tuple):
            units_tuple = units
        else:
            raise TypeError("Argument 'units' must be either a string or tuple")

        if not (set(units_tuple) <= set(self._VALID_UNITS)):
            raise ValueError("One or more units are invalid")

        self._since = since
        self._units = units_tuple

    def convert(self, *field_arrays):
        """Apply the datetime conversion.

        Parameters
        ----------
        field_arrays : list of NumPy array
          list of decoded packet field values, each must have at least one
          dimension

        Returns
        -------
        converted : NumPy array of object (holding datetimes)
          converted form of the decoded packet field values

        Raises
        ------
        ValueError
          Too many or too few units were provided, as compared to the
          input field arrays sent.
        """
        assert len(field_arrays) > 0, "Must have at least one input field"

        converted = []

        for field_values in zip(*field_arrays):
            converted_time = self._since

            for unit, offset_raw in zip(self._units, field_values):
                offset_raw = float(offset_raw)

                if unit == "days":
                    converted_time += timedelta(days=offset_raw)
                elif unit == "hours":
                    converted_time += timedelta(hours=offset_raw)
                elif unit == "minutes":
                    converted_time += timedelta(minutes=offset_raw)
                elif unit == "seconds":
                    converted_time += timedelta(seconds=offset_raw)
                elif unit == "milliseconds":
                    converted_time += timedelta(seconds=offset_raw / self._MILLISECONDS_PER_SECOND)
                elif unit == "microseconds":
                    converted_time += timedelta(seconds=offset_raw / self._MICROSECONDS_PER_SECOND)
                elif unit == "nanoseconds":
                    converted_time += timedelta(seconds=offset_raw / self._NANOSECONDS_PER_SECOND)

            converted.append(converted_time)

        converted = np.array(converted, dtype=object)

        return converted
