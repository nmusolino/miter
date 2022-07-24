#!/usr/bin/env python
# Copyright (c) 2022, Nicholas Musolino
#
# Distributed under the 3-clause BSD license, see accompanying file LICENSE
# or https://github.com/nmusolino/miter for details.

from __future__ import annotations

from setuptools import setup  # isort:skip

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension  # isort:skip

# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

CXX_STD = 17
ext_modules = [
    Pybind11Extension(
        "miter._seqtools",
        ["src/seqtools.cpp"],
        cxx_std=CXX_STD,
    ),
    Pybind11Extension(
        "miter._itertools",
        ["src/itertools.cpp"],
        cxx_std=CXX_STD,
    ),
]


setup(
    ext_modules=ext_modules,
)
