import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# pyloess requires numpy already installed before its installation.
try:
    import numpy
except ImportError:
    import pip
    pip.main(['install', 'numpy>=1.9.2'])

setup(
    name="anomaly-detection",
    version="0.0.1",
    description="A python implementation of https://github.com/twitter/AnomalyDetection",
    packages=find_packages(exclude=['tests.*']),
    install_requires=[
        'pandas>=0.12.0',
        'scipy>=0.15.1',
        'numpy>=1.9.2',
        'pyloess==master'
    ],
    dependency_links=[
        'https://github.com/andreas-h/pyloess/tarball/7415090e00c3987eecc44be2efcfbdaf038656e0#egg=pyloess-master'
    ],
    long_description=read('README.md'),
)
