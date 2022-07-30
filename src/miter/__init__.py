"""
Copyright (c) 2022 Nicholas Musolino. All rights reserved.

miter: Python utility library for iterables and sequences
"""
from __future__ import annotations

import collections
import enum as _enum
import os as _os
import typing
import warnings as _warnings
from typing import Callable, Iterable, Optional, Sequence, TypeVar

from ._version import version as __version__

T = TypeVar("T")


__all__ = (
    "__version__",
    "length",
    "all_equal",
    "unique",
    "indexes",
)

# ITERABLES UTILITIES


def length(iterable: Iterable[T]) -> int:
    """Return the number of elements in ``iterable``.  This may be useful for un-sized
    iterables (without a ``__len__`` function).

    This function potentially consumes the iterable, but when possible, ``len(iterable)``
    is returned without iterating over the argument.

    Examples:
    >>> length(i for i in range(10) if i % 2 == 0)
    5
    >>> r = range(1_000_000_000)
    >>> length(r)
    1000000000
    """
    try:
        maybe_sized = typing.cast(collections.abc.Sized, iterable)
        return len(maybe_sized)
    except TypeError:
        return sum(1 for _ in iterable)


def all_equal(iterable: Iterable[T]) -> bool:
    """Return whether all elements of ``iterable`` are equal.  This returns True for an
    empty iterable.

    Examples:
    >>> all_equal("aaa")
    True
    >>> all_equal("aaab")
    False
    >>> all_equal("")
    True
    """
    iterable = iter(iterable)
    try:
        ref_value = next(iterable)
    except StopIteration:
        return True
    return all(elem == ref_value for elem in iterable)


def unique(
    iterable: Iterable[T], key: Optional[Callable[[T], typing.Hashable]] = None
) -> Iterable[T]:
    """Yield the unique elements in ``iterable``, according to ``key``, preserving order.

    Values provided by ``iterable`` (or if a key is provided, the results of applying
    ``key`` to those values) must be hashable.

    This function uses auxiliary storage in both the Python and C++ implementations.

    Examples:
    >>> list(unique([0, 1, 1, 0, 2, 2, 3, 1]))
    [0, 1, 2, 3]
    """
    if key is None:
        observed_elems = set()
        for elem in iterable:
            if elem not in observed_elems:
                observed_elems.add(elem)
                yield elem
    else:
        observed_keys = set()
        for elem in iterable:
            elem_key = key(elem)
            if elem_key not in observed_keys:
                observed_keys.add(elem_key)
                yield elem


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


# IMPLEMENTATION SELECTION
_IMPL_PREFERENCE_VALID_VALUES = [
    "PREFER_CPP",
    "PREFER_PYTHON",
    "REQUIRE_CPP",
    "REQUIRE_PYTHON",
]

_IMPL_PREFERENCE: str = _os.environ.get("MITER_IMPL", "PREFER_CPP")
if _IMPL_PREFERENCE not in _IMPL_PREFERENCE_VALID_VALUES:
    raise ValueError(
        f"Unrecognized MITER_IMPL value: {_IMPL_PREFERENCE}; "
        f"expected one of: {_IMPL_PREFERENCE_VALID_VALUES!r}"
    )


class Impl(_enum.Enum):
    """Enum indicating a selected implementation."""

    PYTHON_MODULE = "PYTHON_MODULE"
    CPP_EXT_MODULE = "CPP_EXT_MODULE"


PYTHON_MODULE = Impl.PYTHON_MODULE
CPP_EXT_MODULE = Impl.CPP_EXT_MODULE
MITER_IMPL: Impl = PYTHON_MODULE

if _IMPL_PREFERENCE in ("REQUIRE_PYTHON", "PREFER_PYTHON"):
    MITER_IMPL = PYTHON_MODULE
elif _IMPL_PREFERENCE in ("REQUIRE_CPP", "PREFER_CPP"):
    try:
        from miter._miter import (  # type: ignore[misc] # pylint: disable=E0401,W0611,E0611  # noqa: F811
            all_equal,
            indexes,
            length,
            unique,
        )

        MITER_IMPL = CPP_EXT_MODULE
    except ImportError:
        if _IMPL_PREFERENCE == "REQUIRE_CPP":
            raise

        assert _IMPL_PREFERENCE == "PREFER_CPP"
        _warnings.warn(
            "Miter C++ extension module not available; falling back to pure Python implementation."
        )
else:
    raise AssertionError("Reached location logically unreachable.")

del _IMPL_PREFERENCE


def is_implementation_cpp_extension_module() -> bool:
    """Return whether ``miter`` is using the C++ extension module as its implementation."""
    return MITER_IMPL == CPP_EXT_MODULE


def is_implementation_pure_python_module() -> bool:
    """Return whether ``miter`` is using this pure Python module as its implementation."""
    return MITER_IMPL == PYTHON_MODULE
