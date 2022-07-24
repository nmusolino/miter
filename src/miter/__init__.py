"""
Copyright (c) 2022 Nicholas Musolino. All rights reserved.

miter: Python utility library for iterables and sequences
"""
from __future__ import annotations

import enum as _enum
import functools as _functools
import os as _os
import warnings as _warnings

from ._version import version as __version__

__all__ = ("__version__",)


class Impl(_enum.Enum):
    """Enum indicating a selected implementation."""

    PYTHON_SOURCE = 0
    CPP_EXTENSION = 1


def all_cpp_modules_available() -> bool:
    """Return whether C++ extension implementations are available for all `miter` modules."""
    try:
        import miter._seqtools  # pylint: disable=W0611,C0415 # noqa: F401

        return True
    except ImportError:
        return False


def _selected_implementation(preference: str) -> Impl:
    """Return the implementation corresponding to `preference`, which should be one
    of:   'PYTHON_SOURCE', 'CPP_EXTENSION', 'PREFER_PYTHON_SOURCE', OR 'PREFER_CPP_EXTENSION'.

    Examples:
    >>> _selected_implementation("PYTHON_SOURCE")
    <Impl.PYTHON_SOURCE: 0>
    >>> _selected_implementation("CPP_EXTENSION")
    <Impl.CPP_EXTENSION: 1>

    # This assumes that the CPP extension module is available.
    >>> _selected_implementation("PREFER_CPP_EXTENSION")
    <Impl.CPP_EXTENSION: 1>
    """
    canon_pref: str = preference.upper()
    if canon_pref in ("PYTHON_SOURCE", "PREFER_PYTHON_SOURCE"):
        return Impl.PYTHON_SOURCE
    if canon_pref == "CPP_EXTENSION":
        if not all_cpp_modules_available():
            _warnings.warn(
                f"Miter C++ extension module(s) not available, and selected implementation is {preference!r}. Future imports may fail."
            )
        return Impl.CPP_EXTENSION
    if canon_pref == "PREFER_CPP_EXTENSION":
        if not all_cpp_modules_available():
            _warnings.warn(
                "Miter C++ extension module(s) not available; falling back to pure Python."
            )
            return Impl.PYTHON_SOURCE

        return Impl.CPP_EXTENSION

    raise ValueError(f"Unrecognized implementation selection: {preference!r}")


@_functools.lru_cache(maxsize=1)
def implementation() -> Impl:
    """Return the implementation to use, based on the 'MITER_IMPLEMENTATION' environment variable."""
    return _selected_implementation(
        _os.environ.get("MITER_IMPLEMENTATION", "PREFER_CPP_EXTENSION")
    )
