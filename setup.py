import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pybughive",
    version="1.0.0",
    author="Gábor Antal",
    author_email="antal@inf.u-szeged.hu",
    description="PyBugHive is a benchmark of 105 real, manually validated bugs from 10 Python projects",
    license="BSD",
    keywords="bug database, bug dataset, benchmark, Python, real bugs, reproducibility, manually curated bugs",
    url="http://packages.python.org/placeholder",
    packages=['model'],
    long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'pybughive=pybughive:main',
        ],
    },
)
