.. _customization:

**************************************
Customization and Global Configuration
**************************************

The :file:`config.yml` file
===========================

This package uses a :file:`config.yml` configuration file to customize
certain properties. ccsdspy packages look for this configuration file
in a platform-specific directory, which you can see the path for by running::

  >>> import ccsdspy
  >>> ccsdspy.print_config()  # doctest: +SKIP

Using your own :file:`config.yml` file
======================================
To maintain your own customizations, you must place your customized :file:`config.yml` inside the appropriate configuration folder (which is based on the operating system you are working on). The `AppDirs module <https://pypi.org/project/appdirs/>`_ provided by the `sunpy` package is used to determine where to look for your configuration file.

.. warning::
    Do not edit the config.yml file directly in the Python package as it will get overwritten every time you re-install or update the package.

You can copy the file below, customize it, and then place your customized :file:`config.yml` file inside your config folder.
You can run the following code to see where to place it on your specific machine as well:

.. doctest::

  >>> ffrom ccsdspy.config import _get_user_configdir
  >>> print(_get_user_configdir())

.. note:: 
  For more information on where to place your configuration file depending on your operating system, you can refer to the `AppDirs Python package <https://pypi.org/project/appdirs/>`_.

A sample config.yml file
--------------------------------------------------------------------

.. only:: html

.. literalinclude:: ../../ccsdspy/data/config.yml