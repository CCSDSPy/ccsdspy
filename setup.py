#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
from setuptools import setup

with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()

PACKAGENAME = 'ccsdspy'
DESCRIPTION = 'IO Interface for Reading CCSDS Data in Python.'
AUTHOR = 'Daniel da Silva'
AUTHOR_EMAIL = ''
LICENSE = 'unknown'
URL = 'http://github.com/ddasilva/ccsdspy'
# VERSION should be PEP440 compatible (http://www.python.org/dev/peps/pep-0440)
VERSION = '0.0.10'

setup(
    name=PACKAGENAME,
    version=VERSION,
    description=DESCRIPTION,
    install_requires=[
        "numpy"
    ],
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=['ccsdspy'],
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable  ",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ]
)
