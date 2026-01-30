.. _logging:

**************
Logging System
**************

.. note::

    The CCSDSPy logging system is partially based on the Astropy logging system including some of the documentation shown here.

Overview
========

The CCSDSPy logging system makes use of the Python logger system and provides flexibility in deciding
which messages to show, which to send them to a file and a way to capture them.

All messages from CCSDSPy are issued using the logger system and there are no direct ``print()`` calls or use of the ``warnings`` module.
Messages can have one of several levels:

* DEBUG: Detailed information, typically of interest only when diagnosing
  problems.

* INFO: An message conveying information about the current task, and
  confirming that things are working as expected

* WARNING: An indication that something unexpected happened, and that user
  action may be required.

By default, INFO and WARNING messages are displayed, and are sent to a
log file located at ``~/ccsdspy.log`` (if the file is writeable).

Configuring the logging system
==============================

The logging system can be configured using the configuration file as described in `Using the configuration file`_ below,

Context managers
================

In some cases, you may want to capture the log messages, for example to check
whether a specific message was output, or to log the messages from a specific
section of code to a separate file. Both of these are possible using context managers.

To add the log messages to a list, first import the logger if you have not
already done so::

    from ccsdspy import log

then enclose the code in which you want to log the messages to a list in a
``with`` statement::

    with log.log_to_list() as log_list:
        # your code here

In the above example, once the block of code has executed, ``log_list`` will
be a Python list containing all the CCSDSPy logging messages that were raised.
Note that messages continue to be output as normal.

Similarly, you can output the log messages of a specific section of code to a
file using::

    with log.log_to_file('myfile.log'):
        # your code here

which will add all the messages to ``myfile.log`` (this is in addition to the
overall log file mentioned in `Using the configuration file`_).

While these context managers will include all the messages emitted by the
logger (using the global level set by ``log.setLevel``), it is possible to
filter a subset of these using ``filter_level=``, and specifying one of
``'DEBUG'``, ``'INFO'``, ``'WARN'``, ``'ERROR'``. Note that if
``filter_level`` is a lower level than that set via ``setLevel``, only
messages with the level set by ``setLevel`` or higher will be included (i.e.
``filter_level`` is only filtering a subset of the messages normally emitted
by the logger).

Using the configuration file
============================

Options for the logger can be set in the ``[logger]`` section
of the CCSDSPy configuration file. For more information on the configuration file, see :ref:`customization`.
