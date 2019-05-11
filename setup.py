#! /usr/bin/env python3

from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='msiem',
    description="McAfee SIEM Command Line Interface and Python API",
    url='https://github.com/tristanlatr/msiem',
    version='0.0.4',
    packages=['msiem',],
    entry_points = {
        'console_scripts': ['msiem=msiem.command:main'],
    },
    install_requires=[
          'requests','tqdm','PTable'
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