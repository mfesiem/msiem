try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='msiem',
    url='https://github.com/tristanlatr/msiem',
    version='0.0.1',
    packages=['msiem',],
    entry_points = {
        'console_scripts': ['msiem=msiem.command:main'],
    },
    install_requires=[
          'requests',
    ],
    license='The MIT License',
    long_description=open('README.md').read(),
    test_suite="tests"
)