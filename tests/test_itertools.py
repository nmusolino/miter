from __future__ import annotations

from miter import itertools as mitertools


def test_length():
    assert mitertools.length([]) == 0
    assert mitertools.length([0]) == 1
    assert mitertools.length([0] * 5) == 5
    assert mitertools.length("abcde") == 5
    # Test `mitertools.length()` with a non-sequence iterable.
    assert mitertools.length(i for i in range(100) if (i % 2 == 0)) == 50


def test_length_for_sequence():
    N = 1_000_000_000
    assert mitertools.length(range(N)) == N
