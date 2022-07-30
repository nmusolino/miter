from __future__ import annotations

import itertools

import pytest

import miter


def test_length():
    assert miter.length([]) == 0
    assert miter.length([0]) == 1
    assert miter.length([0] * 5) == 5
    assert miter.length("abcde") == 5
    # Test `miter.length()` with a non-sequence iterable.
    assert miter.length(i for i in range(100) if (i % 2 == 0)) == 50


def test_length_for_sequence():
    N = 1_000_000_000
    assert miter.length(range(N)) == N


def test_unique():
    unique = miter.unique
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
    unique = miter.unique
    with pytest.raises(TypeError):
        list(unique([[], [1], [2]]))
