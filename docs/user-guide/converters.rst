.. _converters:

********************************
Post-Processing Transformations
********************************

Overview
========
Post-processing transformations are done through the Converters API, exposed through the `~ccsdspy.converters` module. Using Converters, one can create new fields transformed from another field. Examples including applying calibration curves, replacing enumerated values with strings, or converting your own time definition to a `datetime` instance. The following converters are built in, and you can write your own converter by extending the `~ccsdspy.converters.Converter` class (more on this below). When new fields are transformed from other fields, they are created as new entries in the returned dictionary.

#. Polynomial Transformation (`~ccsdspy.converters.PolyConverter`)

   This applies a polynomial function to each value, using user-defined coeffients.
   
#. Linear Transformation (`~ccsdspy.converters.LinearConverter`)

   This applies a linear transformation (`y = mx + b`) to each value, using a user-defined slope and intercept.
   
#. Enumerated Values Transformation (`~ccsdspy.converters.EnumConverter`)   
   
   This applies a dictionary replacement of integers to strings. For instance, you can use this to replace `0` with `"DISABLED"`, `1` with `"ENABLED"`, and `2` with `"STANDBY"`.


Using a Built-In Transformations
*************************************
An example of using a built in transformation to apply a linear transformation to a first field and apply a enumerated values transformation to a secondary field is below.

.. code-block:: python
		
    from ccsdspy import FixedLength, converters
   
    pkt = FixedLength([
        PacketField(name="FirstField", data_type="uint", bit_length=8),
        PacketField(name="SecondField", data_type="uint", bit_length=8),
    ])
    pkt.add_converter(
        "FirstField",
	"FirstField_Converted",
	LinearConverter(slope=1.2, intercept=0.4)
    )
    pkt.add_converter(
        "SecondField",
	"SecondField_Converted",
	converters.EnumConverter({
	    0: "DISBLED",
	    1: "ENABLED",
	    2: "STANDBY"
	})
    )
    
    result = pkt.load("MyCCSDS.bin")
		
    print(result["FirstField_Converted"])
    print(result["SecondField_Converted"])    


Creating User-Defined Transformations
*************************************
Users can create their own user-defined transformations by extending the `~ccsdspy.converters.Converter` class and overriding the `convert_many(field_array)` function. This function accepts as an argument the decoded input field array and returns the converted array. If more convinient, one may instead override the `convert_one(field_value)` function which accepts a single decoded field value and returns a single converted value.

Below is an example of creating a user-defined transformation to return False if the value is equal to zero, and True if the value is greater than zero.

.. code-block:: python
		
    from ccsdspy import FixedLength, converters

    class CustomConverter(converters.Converter):
        def convert_many(field_array):
            return (field_array > 0)
    
    pkt = FixedLength([
        PacketField(name="MyField", data_type="uint", bit_length=8)
    ])
    pkt.add_converter(
        "MyField",
	"MyField_Converted",
	CustomConverter()
    )
    
    result = pkt.load("MyCCSDS.bin")
		
    print(result["MyField_Converted"])
