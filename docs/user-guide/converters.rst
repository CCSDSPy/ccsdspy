.. _converters:

********************************
Post-Processing Transformations
********************************

Post-processing transformations are done through the Converters API, exposed through the `~ccsdspy.converters` module. Using Converters, one can create new fields transformed from another field. Examples including applying calibration curves, replacing enumerated values with strings, or converting your own time definition to a `datetime` instance. The following converters are built in, and you can write your own converter by extending the `~ccsdspy.converters.Converter` class (more on this below). When new fields are transformed from other fields, they are created as new entries in the returned dictionary.

#. Polynomial Transformation (`~ccsdspy.converters.PolyConverter`)

   This applies a polynomial function to each value, using user-defined coeffients.
   
#. Linear Transformation (`~ccsdspy.converters.LinearConverter`)

   This applies a linear transformation (`y = mx + b`) to each value, using a user-defined slope and intercept.
   
#. Enumerated Values Transformation (`~ccsdspy.converters.EnumConverter`)   
   
   This applies a dictionary replacement of integers to strings. For instance, you can use this to replace `0` with `"DISABLED"`, `1` with `"ENABLED"`, and `2` with `"STANDBY"`.

#. Datetime Transformation (`~ccsdspy.converters.DatetimeConverter`)

   This converts fields to datetime instances, computed using offset(s) from a reference time. The offsets can span multiple fields (for example, one a coarse time, and another for a fine time). If the reference time has a timezone, the result will too.

#. Stringify Bytes Transformation (`~ccsdspy.converters.StringifyBytesConverter`)

   This converts byte arrays or multi-byte numbers to strings in numeric representations such as binary, hexidecimal, or octal.
   
.. contents::
   :depth: 2

Using a Built-In Transformations
================================
An example of using a built in transformation to parse time, apply a linear transformation to a first field, and apply a enumerated values transformation to a secondary field is below.

.. code-block:: python
		
    from ccsdspy import FixedLength, converters
   
    pkt = FixedLength([
	PacketField(name="CoarseTime",  data_type="uint", bit_length=24)
        PacketField(name="FineTime",    data_type="uint", bit_length=48)
        PacketField(name="FirstField",  data_type="uint", bit_length=8),
        PacketField(name="SecondField", data_type="uint", bit_length=8),
    ])

    pkt.add_converted_field(
        ("CoarseTime", "FineTime"),
	"Time_Converted",
	converters.DatetimeConverter(
	   since=datetime(1970, 1, 1),
           units=("seconds", "nanoseconds"),
	)
    )		
    pkt.add_converted_field(
        "FirstField",
	"FirstField_Converted",
	converters.LinearConverter(slope=1.2, intercept=0.4)
    )
    pkt.add_converted_field(
        "SecondField",
	"SecondField_Converted",
	converters.EnumConverter({
	    0: "DISBLED",
	    1: "ENABLED",
	    2: "STANDBY"
	})
    )
    
    result = pkt.load("MyCCSDS.bin")

    print(result["Time_Converted"])
    print(result["FirstField_Converted"])
    print(result["SecondField_Converted"])    


Creating User-Defined Transformations
=====================================
Users can create their own user-defined transformations by extending the `~ccsdspy.converters.Converter` class and overriding the `convert(*field_arrays)` function. This function accepts as many arguments argument as input fields were provided when the converter was added.

Below is an example of creating a user-defined transformation to return False if the value is equal to zero, and True if the value is greater than zero.

.. code-block:: python
		
    from ccsdspy import FixedLength, converters

    class CustomConverter(converters.Converter):
        def __init__(self):
	    pass
        def convert(field_array):
            return (field_array > 0)
    
    pkt = FixedLength([
        PacketField(name="MyField", data_type="uint", bit_length=8)
    ])
    pkt.add_converted_field(
        "MyField",
	"MyField_Converted",
	CustomConverter()
    )
    
    result = pkt.load("MyCCSDS.bin")
		
    print(result["MyField_Converted"])
