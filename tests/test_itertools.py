from __future__ import annotations

import itertools

import pytest

import miter


def test_all_unique():
    # Test some simple sequences.
    assert miter.all_unique([])
    assert miter.all_unique([0])
    assert miter.all_unique([0, 1, 2])
    assert miter.all_unique(range(100))
    assert not miter.all_unique([0, 0])
    assert not miter.all_unique([0] * 1_000)

    # Test with key.
    assert miter.all_unique(range(100), key=lambda i: i % 100)
    assert not miter.all_unique(range(100), key=lambda i: i % 10)

    # Test with strings
    assert miter.all_unique("abcdA")
    assert not miter.all_unique("abcdA", key=str.upper)


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
