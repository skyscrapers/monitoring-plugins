#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re
import sys

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


requires = [
    'boto3'
]


if sys.version_info[0] == 2:
    # concurrent.futures is only in python3, so for
    # python2 we need to install the backport.
    requires.append('futures>=2.2.0,<4.0.0')



setup(
    name='skymonitoringplugins',
    version="1.3.1",
    description='Skyscrapers monitoring tools',
    author='skyscrapers',
    scripts=[],
    include_package_data=True,
    install_requires=requires,
)