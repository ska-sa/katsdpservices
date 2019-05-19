#!/usr/bin/env python
from setuptools import setup, find_packages

tests_require = ['mock', 'nose', 'unittest2', 'six', 'katsdptelstate',
                 'aiomonitor; python_version>="3"']

setup(
    name="katsdpservices",
    description=("common code used by services that make up the telescope system, "
                 "such as a common logging setup"),
    author="Bruce Merry",
    author_email="bmerry@ska.ac.za",
    packages=find_packages(),
    setup_requires=["katversion"],
    install_requires=["netifaces", "pygelf"],
    tests_require=tests_require,
    extras_require={
        "argparse": ["katsdptelstate"],
        "asyncio": ["tornado", "trollius"],
        "aiomonitor": ["aiomonitor"],
        "test": tests_require},
    use_katversion=True
)
