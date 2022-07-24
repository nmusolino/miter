"""Utility functions for sequences."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, TypeVar

import miter

T = TypeVar("T")


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


if miter.implementation() == miter.Impl.CPP_EXTENSION:

    from miter._seqtools import (  # type: ignore[misc]  # pylint: disable=E0401,W0611,E0611  # noqa: F401, F811
        indexes,
    )
