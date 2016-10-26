import sys
import os
try: from setuptools import setup
except ImportError: from distutils.core import setup

import versioneer

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='mkauthlist',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Set of simple tools for working in DES.",
    url='https://github.com/kadrlica/mkauthlist',
    author='Alex Drlica-Wagner',
    author_email='kadrlica@fnal.gov',
    license='MIT',
    scripts = ['bin/mkauthlist'],
    packages = ['mkauthlist'],
    install_requires=[
        'python >= 2.7.0',
        'numpy >= 1.6.1',
    ],
    platforms='any',
    keywords='latex des',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
    ]
)
