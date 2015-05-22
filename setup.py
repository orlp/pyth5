#!/usr/bin/env python3

import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open("pyth_lang/pyth.py").read(),
    re.M).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="pyth-lang",
    packages=["pyth_lang"],
    entry_points={"console_scripts": ["pyth=pyth_lang.pyth:cli"]},
    version=version,
    description="Pyth programming language.",
    long_description=long_descr,
    license="zlib",
    author="isaacg",
    author_email="isaacg@mit.edu",
    url="https://github.com/isaacg1/pyth",
    classifiers=[
        "License :: OSI Approved :: zlib/libpng License",
        "Programming Language :: Other",
        "Topic :: Software Development :: Interpreters",
    ]
)
