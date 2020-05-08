#!/usr/bin/env python

import os
from setuptools import setup, find_packages

tests_require = ['nose', 'katsdptelstate', 'aiomonitor']
long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name="katsdpservices",
    description=("Common code used by services that make up the MeerKAT Science Data Processor, "
                 "such as a common logging setup"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="MeerKAT SDP team",
    author_email="sdpdev+katsdpservices@ska.ac.za",
    url='https://github.com/ska-sa/katsdpservices',
    packages=find_packages(),
    setup_requires=["katversion"],
    install_requires=["netifaces", "pygelf>=0.3.6"],
    tests_require=tests_require,
    extras_require={
        "argparse": ["katsdptelstate"],
        "aiomonitor": ["aiomonitor"],
        "test": tests_require},
    python_requires='>=3.5',
    use_katversion=True
)
