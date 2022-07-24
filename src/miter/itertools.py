"""Utility functions for sequences."""

from __future__ import annotations

import collections
import typing
from typing import Iterable, TypeVar

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


if miter.implementation() == miter.Impl.CPP_EXTENSION:

    from miter._itertools import (  # pylint: disable=E0401,W0611,E0611  # noqa: F401, F811
        length,
    )
