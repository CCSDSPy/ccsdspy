.. _spac-kit-installation:

************
Installation
************

Requirements
============

Python 3.12 or higher

For Users
=========

Create a virtual environment (recommended):

.. code-block:: bash

   python3 -m venv .venv
   source .venv/bin/activate

Install a plugin first, for example:

.. code-block:: bash

   pip install spac-kit-europa-clipper

Then install SPaC-Kit:

.. code-block:: bash

   pip install spac-kit

Verify installation:

.. code-block:: bash

   spac-ls  # Should list available packet definitions

For Developers
==============

Clone and set up:

.. code-block:: bash

   git clone https://github.com/CCSDSPy/SPaC-Kit.git
   cd SPaC-Kit

   # Create environment with Poetry
   poetry env use python3.12
   poetry install --with dev

   # Install pre-commit hooks
   pre-commit install && pre-commit install -t pre-push

Use with Poetry:

.. code-block:: bash

   poetry run spac-parse --help
   poetry run pytest

Update lock file before committing:

.. code-block:: bash

   poetry lock

Contributing
============

Development should be done on a feature branch. When your changes are ready for review, open a pull request (PR) against the main branch.
Automated tests and linting are run on all PRs — make sure both pass before requesting a review.


Building and Publishing
=======================

Update version in ``pyproject.toml``, then

.. code-block:: bash

   # Tag and push
   git tag vX.Y.Z
   git push origin main --tags

   # Build
   python3 -m pip install --upgrade build
   rm -rf dist/
   python3 -m build

   # Publish
   pip install twine
   twine upload dist/*
