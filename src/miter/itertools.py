"""Utility functions for iterables."""

from __future__ import annotations

import collections
import typing
from typing import Callable, Iterable, Optional, TypeVar

import miter

T = TypeVar("T")


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


if miter.implementation() == miter.Impl.CPP_EXTENSION:

    from miter._itertools import (  # type: ignore[no-redef,attr-defined] # pylint: disable=E0401,W0611,E0611  # noqa: F401, F811
        length,
        unique,
    )
