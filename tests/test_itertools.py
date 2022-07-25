from __future__ import annotations

import itertools

import pytest

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


def test_unique():
    unique = mitertools.unique
    # Test with zero elements.
    assert list(unique([])) == []
    # Test with repeated elements.
    assert list(unique([0, 0, 0])) == [0]
    assert list(unique(itertools.islice(itertools.repeat(1), 100))) == [1]
    # Test with distinct elements
    assert list(unique(range(10))) == list(range(10))
    # Test with mixture of repeated and distinct elements.
    assert list(unique("abracadabra")) == ["a", "b", "r", "c", "d"]


def test_unique_unhashable_elements():
    unique = mitertools.unique
    with pytest.raises(TypeError):
        list(unique([[], [1], [2]]))
