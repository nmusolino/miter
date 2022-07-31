from __future__ import annotations

import itertools

import pytest

import miter


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
