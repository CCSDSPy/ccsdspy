.. _devguide:

***************
Developer Guide
***************

Welcome to the Developer Guide. Thank you for your interest in contributing to this project!
The following standards are based on those provided by the `sunpy <https://github.com/sunpy/sunpy>`__.
We would like to thank their contribution to the community.

Installing for development
==========================
To install this package for local development, first clone this package from github using your favorite git gui or with the command::

    git clone git@github.com:ccsdspy/ccsdspy.git

Then go into the directory and install the package for editing with the following command::

    pip install -e '.[dev]'

This will include all of the development dependencies. 
If you also need to build the documentation locally use the following command::

    pip install -e '.[docs]'

Code Standards
==============
All developers should read and abide by the following standards.
Code which does not follow these standards closely will generally not be accepted.

We try to closely follow the coding style and conventions proposed by `Astropy <https://docs.astropy.org/en/stable/development/codeguide.html#coding-style-conventions>`_.

Language Standard
-----------------

* All code must be compatible with Python 3.6 and later.

* The new Python 3 `f-string <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`__ formatting style should be used (i.e.
  ``f"{spam:s}"`` instead of ``"%s" % "spam"`` or using `format() <https://docs.python.org/3/library/stdtypes.html#str.format>`__.

Coding Style/Conventions
------------------------

* The code will follow the standard `PEP8 Style Guide for Python Code <https://www.python.org/dev/peps/pep-0008/>`_.
  In particular, this includes using only 4 spaces for indentation, and never tabs.

* **Follow the existing coding style** within a file and avoid making changes that are purely stylistic.
  Please try to maintain the style when adding or modifying code.

* Following PEP8's recommendation, absolute imports are to be used in general.
  We allow relative imports within a module to avoid circular import chains.

* The ``import numpy as np``, ``import matplotlib as mpl``, and ``import matplotlib.pyplot as plt`` naming conventions should be used wherever relevant.
  
* ``from packagename import *`` should never be used (except in ``__init__.py``)

* Classes should either use direct variable access, or Python's property mechanism for setting object instance variables.

* Classes should use the builtin `super` function when making calls to methods in their super-class(es) unless there are specific reasons not to.
  `super` should be used consistently in all subclasses since it does not work otherwise.

* Multiple inheritance should be avoided in general without good reason.

* ``__init__.py`` files for modules should not contain any significant implementation code. ``__init__.py`` can contain docstrings and code for organizing the module layout.

Private code
------------

It is often useful to designate code as private, which means it is not part of the user-facing API, only used internally
Private code modification do not generally require major version updates according to semantic versioning.
Any classes, functions, or variables that are private should either:

- Have an underscore as the first character of their name, e.g., ``_my_private_function``.
- If you want to do that to entire set of functions in a file, name the file with a underscore as the first character, e.g., ``_my_private_file.py``.

Utilities
---------

Within this repository, utility functions are placed in the `util.py` file.
These functions can be private or public.
If these might be useful for other modules are user-focused, they should be made public.


Linting and Code Formatting
===========================
We enforce a minimum level of code style with our continuous integration testing.
This project makes use of `black <https://github.com/psf/black>`__ to format all code.
To run this yourself before submitting code just use the following command::

    black ccsdspy

We also use `flake8 <https://flake8.pycqa.org/>`__ for linting. To run it locally::

    flake8 ccsdspy --count --select=E9,F63,F7,F82 --show-source --statistics


Testing and Coverage
====================
It is expected that all new code and functionality will also provide tests to ensure expected behavior.
We use `pytest <https://docs.pytest.org/>`__ and all tests files should be added to the `tests` folder.
Test coverage is determined for every merge request and if the coverage percentage decreases significantly new code will generally not be accepted.


Documentation
=============

* American English is the default language for all documentation strings and inline commands.
  Variables names should also be based on English words.

* Documentation strings must be present for all public classes/methods/functions.
  Additionally, examples or tutorials for new functionality are strongly recommended.

* Write usage examples in the docstrings of all classes and functions whenever possible.
  These examples should be short and simple to reproduce.
  These examples should, whenever possible, be in the `doctests <https://docs.python.org/3/library/doctest.html>`__ format and will be executed as part of the test suite.


Releases
========

Incrementing Version Numbers
----------------------------

This package uses `Semantic Versioning <https://semver.org/>`__.
A version number for a release should be of the form ``X.Y.Z``.
This package is configured to use `setuptools_scm <https://pypi.org/project/setuptools-scm/>`__ to manage version numbers which uses git tags 
The version information is stored in a automatically generated file called `_version.py`.
This file is only generated when the package is imported (or re-imported).

Assuming that your new release is 0.2.0, to mark a new release of your package in your git history run:

.. code-block:: console

   $ git tag -a v0.2.0 -m "Release version 0.2.0"

Here we use the convention of prepending release tags with ``v``.

If you now re-import your package (to regenerate ``_version.py``) and print ``ccsdspy.__version__`` it should say
``0.2.0``.

Do not make any other commits at this point because as soon as you do, the version will be automatically incremented to ``0.2.1.dev``.

Building Source Distributions
-----------------------------

Now that have tagged your release, you need to build what is called a "source
distribution" to upload to `PyPI <https://pypi.org/>`__ or the Python Package
Index. To create this, you can run the following command which uses `pypa-build <https://pypa-build.readthedocs.io/en/latest/>`__ to
build your sdist in the isolated environment specified in `pyproject.toml`:

.. code-block:: console

   $ pip install build
   $ python -m build --sdist --outdir dist .


Publishing to PyPI
------------------

Now you have created the sdist to be uploaded to PyPI you can upload it with the
`twine <https://pypi.org/project/twine/>`__ package:

.. code-block:: console

   $ pip install twine
   $ twine upload dist/my_package*.tar.gz

This should ask you for your PyPI account details, and will create your project
on PyPI if it doesn't already exist.
