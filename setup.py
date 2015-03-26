# Copyright (C) 2014  Leo Singer
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# Bootstrap setuptools installation.
try:
    import pkg_resources
    pkg_resources.require("setuptools >= 0.7")
except:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup
import gcn
import sys

install_requires = []
python_version_tuple = sys.version_info[:2]
if python_version_tuple == (2, 6) or python_version_tuple == (3, 1):
    install_requires += ['lxml']

setup(
    name='pygcn',
    version='0.1.6',
    author='Leo Singer',
    author_email='leo.singer@ligo.org',
    description=gcn.__doc__.splitlines()[1],
    long_description=gcn.__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering :: Astronomy'
    ],
    license='GPL-2+',
    url='https://github.com/lpsinger/pygcn',
    packages=['gcn'],
    scripts=['bin/pygcn-listen', 'bin/pygcn-serve'],
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=install_requires
)