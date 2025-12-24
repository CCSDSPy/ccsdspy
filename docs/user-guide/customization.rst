.. _customization:

**************************************
Customization and Global Configuration
**************************************

The :file:`config.yml` file
===========================

This package uses a :file:`config.yml` configuration file to customize
certain properties. You can control a number of key features such as
where your data will download to. ccsdspy packages look for this configuration file
in a platform-specific directory, which you can see the path for by running::

  >>> import ccsdspy
  >>> ccsdspy.print_config()  # doctest: +SKIP

Using your own :file:`config.yml` file
======================================
To maintain your own customizations, you must place your customized :file:`config.yml` inside the appropriate configuration folder (which is based on the operating system you are working on). The `AppDirs module <https://github.com/sunpy/sunpy/blob/main/sunpy/extern/appdirs.py>`_ provided by the `sunpy` package is used to determine where to look for your configuration file.

.. warning::
    Do not edit the config.yml file directly in the Python package as it will get overwritten every time you re-install or update the package.

You can copy the file below, customize it, and then place your customized :file:`config.yml` file inside your config folder.

If you work in our developer environment you can place your configuration file in this directory:

.. code-block:: bash

  /home/vscode/.config/ccsdspy/

You can also specify the configuration directory by setting the environment variable `ccsdspy_CONFIGDIR` to the path of your configuration directory. For example, you can set the environment variable in your terminal by running:

.. code-block:: bash

  export ccsdspy_CONFIGDIR=/path/to/your/config/dir

If you do not use our developer environment, you can run the following code to see where to place it on your specific machine as well:

.. doctest::

  >>> from ccsdspy import util
  >>> print(util.config._get_user_configdir())
  /home/vscode/.config/ccsdspy

.. note:: 
  For more information on where to place your configuration file depending on your operating system, you can refer to the `AppDirs module docstrings <https://github.com/sunpy/sunpy/blob/1459206e11dc0c7bfeeeec6aede701ca60a8630c/sunpy/extern/appdirs.py#L165>`_.

A sample config.yml file
--------------------------------------------------------------------

.. only:: html

    `(download) <../_static/config.yml>`__

.. literalinclude:: ../../ccsdspy/data/config.yml