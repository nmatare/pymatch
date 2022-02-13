#!/usr/bin/python
# -*- coding: utf-8 -*-
# "Author: Nathan Matare <nathan.matare@gmail.com>"
#
# """ Setup and Installation """

from setuptools import setup, find_packages
import versioneer
import os

name = 'pymatch'

maintainers = {'Nathan Matare': 'nathan.matare@gmail.com'}

# Should be one of:
# RELEASE_STATUS = 'Development Status :: 1 - Planning'
RELEASE_STATUS = 'Development Status :: 2 - Pre-Alpha'
# RELEASE_STATUS = 'Development Status :: 3 - Alpha'
# RELEASE_STATUS = 'Development Status :: 4 - Beta'
# RELEASE_STATUS = 'Development Status :: 5 - Production/Stable'
# RELEASE_STATUS = 'Development Status :: 6 - Mature'
# RELEASE_STATUS = 'Development Status :: 7 - Inactive'

PYTHON_VERSION = '==3.7.11'


with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')


install_requires = [os.path.expandvars(v) for v in install_requires]


tests_require = [
    'pytest==6.2.4',
    'versioneer==0.18',
    'pre-commit==2.2.0',
    'pyinstrument==4.1.1',
]


setup(
    name=name,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author=set(maintainers),
    author_email=set(maintainers.values()),
    license=None,
    url=f'https://github.com/nmatare/{name}/',
    classifiers=[
        RELEASE_STATUS,
        'Intended Audience :: Developers',
        f'Programming Language :: Python :: {PYTHON_VERSION}',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    include_package_data=True,
    package_data=None,
    install_requires=install_requires,
    packages=find_packages(),
    python_requires=PYTHON_VERSION,
    extras_require={'tests': tests_require},
    zip_safe=False,
)

# EOF
