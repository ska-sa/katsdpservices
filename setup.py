#!/usr/bin/env python

################################################################################
# Copyright (c) 2017-2020, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

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
    license='Modified BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Astronomy'
    ],
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
