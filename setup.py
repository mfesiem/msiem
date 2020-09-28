#! /usr/bin/env python3

from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

#Version of the project
version = {}
exec((HERE / "msiem" / "__version__.py").read_text(), version)

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='msiem',
    description="McAfee SIEM Command Line Interface",
    url='https://github.com/mfesiem/msiem',
    author='tristanlatr, andywalden',
    version=version['__version__'],
    packages=['msiem',],
    entry_points = {
        'console_scripts': ['msiem=msiem.cli:main'],
    },
    install_requires=[
          'msiempy', 'requests', 'lxml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license='The MIT License',
    long_description=README,
    long_description_content_type="text/markdown"
)