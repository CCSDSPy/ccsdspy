"""This class hold the implementation of the converter system, which applies 
post-process to decoded packet fields. This post-processing includes applying
linear/polynomial calibration curves, dictionary replacement, and time parsing.
"""

import numpy as np


class EnumConverterMissingKey(RuntimeError):
    """During conversion a value was encountered which did not have a
    corresponding key in the replacement dictionary.
    """


class Converter:
    """Base class for all converter objects.

    This class is extended to create converters, and users may extend this
    class to write their own custom converters.

    To write a converter, one must create a subclass and override either the method
    `convert_many(field_array)` or `convert_one(field_array)`. The
    `convert_many(field_array)` method implements the conversion for an entire
    sequence of decoded packet field values in a single call (this is sometimes
    faster), while the `convert_one(field_array)` method implements the
    conversion for a single packet field at a time (this is sometimes easier to
    write).
    """

    def __init__(self):
        raise NotImplementedError("This is a base class not meant to be instantiated directly")

    def convert_many(self, field_array):
        """Convert a sequence of decoded packet field values.

        This default implementation loops over the elements and defers the
        conversion to `self.convert_one(field_array[i])`.

        Parameters
        ----------
        field_array : NumPy array
            decoded packet field values, must have at least one dimension

        Returns
        -------
        converted_field_array : NumPy array
            converted form of the decoded packet field values
        """
        converted_field_array = []

        for i in range(field_array.shape[0]):
            converted = self.convert_one(field_array[i])
            converted_field_array.append(converted)

        # Let NumPy infer the type from the elements.
        converted_field_array = np.array(converted_field_array)

        return converted_field_array

    def convert_one(self, field_value):
        """Convert a singel decoded packet field value.

        Parameters
        ----------
        field_value : object
            a single decoded packet field value

        Returns
        -------
        converted_field_value : object
            converted form of the decoded packet field value
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

    def convert_many(self, field_array):
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
        ValueError
           Either one of the keys of the replacement dictionary is not an
           integer, or one of the values is not a string.
        """
        self._replace_dict = replace_dict

        for key, value in replace_dict.items():
            if not isinstance(key, int):
                raise ValueError(
                    f"Found key in EnumConverter replacement dictionary that is "
                    f"not an integer: {repr(key)}"
                )
            if not isinstance(value, str):
                raise ValueError(
                    f"Found value in EnumConverter replacement dictionary that is "
                    f"not a string: {repr(kevalue)}"
                )

    def convert_many(self, field_array):
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
