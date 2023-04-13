.. _synthetic:

*****************
Synthetic Packets
*****************

Overview
========
It is sometimes necessary or useful to generate synthetic CCSDS packets with known data for testing and validation.
Both `~ccsdspy.FixedLength` and `~ccsdspy.VariableLength` packet types provide this functionality through their respective
:py:meth:`ccsdspy.FixedLength.to_file` and :py:func:`ccsdspy.VariableLength.to_file` methods.
You'll first have to define the packet as usual as if you are going to parse a file with packets in it.

Fixed Length
============
Fixed length packets are ones that only include `~ccsdspy.PacketField` that do not vary in size.
First define the packet,

.. code-block:: python

   import ccsdspy
   from ccsdspy import PacketField

   pkt = ccsdspy.FixedLength([
        PacketField(name="DATAU", data_type="uint", bit_length=32),
        PacketField(name="DATAI", data_type="int", bit_length=16),
        PacketField(name="DATAF", data_type="float", bit_length=64),
        PacketField(name="DATAS", data_type="str", bit_length=8),
        PacketField(name="DATAFLAG", data_type='uint', bit_length=1),
        PacketArray(
            name="SENSOR_GRID",
            data_type="uint",
            bit_length=16,
            array_shape=(32, 32),
            array_order="C",
        )
   ])

Once you've done that you'll have to define a dictionary whose keys are the packet field names and whose values are your data arrays.

.. code-block:: python

    num_packets = 1000
    datau = np.arange(0, num_packets, dtype=np.uint32)
    datai = np.arange(1, num_packets + 1, dtype=np.int16)
    dataf = np.arange(2, num_packets + 2, dtype=np.float64)
    datas = np.arange(97, num_packets + 97, dtype=np.uint8)
    dataflag = np.zeros(num_packets, dtype=np.bool)
    sensor_grid = (
        np.arange(0, num_packets * 32 * 32, dtype=np.uint16)
        .reshape(num_packets, 32, 32)
    )
    data = {
        "DATAU": datau,
        "DATAI": datai,
        "DATAF": dataf,
        "DATAS": datas,
        "DATAFLAG": dataflag,
        "SENSOR_GRID": sensor_grid
    }

If you have a non-standard bit_length (e.g. 6, 14), simply select a dtype that will fit the data (e.g. 8, 16, respectively).
Once you have this data dictionary defined you can write to a file

.. code-block:: python

    pkt_type = 0         # For telemetry (or reporting), set to ‘0’
    apid = 0x084         # the Application process identifier
    sec_header_flag = 0  # set to 0 if secondary header exists
    seq_flag = 0         # Set to 0 if not continuation packet
    pkt.to_file("test.bin", pkt_type, apid, sec_header_flag,
        seq_flag, data)

For a description of the CCSDS header see :ref:`ccsds_standard`.
You can parse the file using the same object if you'd like to check its contents with::

    result = pkt.load("test.bin")

Variable Length
===============
Variable length packets are packets which may have a different length each time.
They include at least one variable length field defined by `~ccsdspy.PacketArray` which can either set `array_shape="expand"` (causing the field to grow to fill the packet) or
`array_shape="other_field"` (causes the field named `other_field` to set the number of elements in this array).

.. code-block:: python

    pkt = VariableLength(
            [
                PacketField(name="DATAU", data_type="uint",
                    bit_length=32),
                PacketArray(
                    name="VARARRAY",
                    data_type="uint",
                    bit_length=8,
                    array_shape="expand",
                ),
            ]
        )

Since the array is a variable length we cannot use a typical `~numpy.ndarray`.
Instead, we can use either a `list` or a `~numpy.ndarray` with `dtype=object` referencing other arrays at each element.
In this example, we will use a list.

.. code-block:: python

    num_packets = 1000
    datau = np.arange(num_packets, dtype=np.uint32)
    data_expand_length = np.random.randint(1, 10, size=num_packets)
    data_expand = []
    for i in range(num_packets):
        data_expand.append(
            np.random.randint(1, 10, size=data_expand_length[i],
                dtype=np.uint8)
            )
    data = {
        "DATAU": datau,
        "DATAEXPAND": data_expand,
    }
    pkt.to_file("test.bin", pkt_type=0, apid=10, sec_header_flag=0,
        seq_flag=0, data=data)

You can parse the file using the same object if you'd like to check its contents with::

    result = pkt.load("test.bin")
