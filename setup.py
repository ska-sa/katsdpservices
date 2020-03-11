#!/usr/bin/env python
from setuptools import setup, find_packages

tests_require = ['nose', 'katsdptelstate', 'aiomonitor']

setup(
    name="katsdpservices",
    description=("common code used by services that make up the telescope system, "
                 "such as a common logging setup"),
    author="MeerKAT SDP team",
    author_email="sdpdev+katsdpservices@ska.ac.za",
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
