#! /usr/bin/env python3

from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='msiem',
    description="McAfee SIEM Command Line Interface",
    url='https://github.com/tristanlatr/msiem',
    author='tristanlatr',
    author_email='trislatr@gmail.com',
    version='0.1.9',
    packages=['msiem',],
    entry_points = {
        'console_scripts': ['msiem=msiem.cli:main'],
    },
    install_requires=[
          'msiempy>=0.2.0'
    ],
    tests_require=[
          'pylint',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license='The MIT License',
    long_description=README,
    long_description_content_type="text/markdown",
    test_suite="tests"
)