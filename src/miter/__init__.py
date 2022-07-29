"""
Copyright (c) 2022 Nicholas Musolino. All rights reserved.

miter: Python utility library for iterables and sequences
"""
from __future__ import annotations

import enum as _enum
import functools as _functools
import os as _os
import warnings as _warnings
from typing import Iterable, Optional, Sequence, TypeVar

from ._version import version as __version__

__all__ = ("__version__",)


T = TypeVar("T")


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


# SEQUENCE UTILITIES


def indexes(
    seq: Sequence[T], value: T, start: Optional[int] = None, end: Optional[int] = None
) -> Iterable[int]:
    """Return an iterator over the indexes of all elements equal to ``value`` in ``sequence``.

    If provided, the ``start`` and ``end`` parameters are interpreted as in slice notation
    and are used to limit the search to a particular subsequence, as in the builtin
    ``list.index()`` method.

    Examples:
    >>> list(indexes("abracadabra", "a"))
    [0, 3, 5, 7, 10]
    >>> list(indexes([0, 1, 2, 3], 2, 1, -1))
    [2]
    """
    n: int = len(seq)  # pylint: disable=C0103
    # Clamp to range [-n, n).
    start_clamped: int = max(-n, min(start or 0, n - 1))
    assert (n == 0) or (-n <= start_clamped < n)
    enum_start: int = start_clamped % n if n else 0
    assert (n == 0) or (0 <= enum_start < n)
    return (i for i, elem in enumerate(seq[start:end], enum_start) if elem == value)


if implementation() == Impl.CPP_EXTENSION:
    from miter._seqtools import (  # type: ignore[misc]  # pylint: disable=E0401,W0611,E0611  # noqa: F401, F811
        indexes,
    )
