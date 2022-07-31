from __future__ import annotations

import itertools
import string

import hypothesis
import pytest
from hypothesis import strategies as st

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


@hypothesis.given(st.iterables(st.integers(), unique=True))
def test_unique_with_unique_iterable(it):
    it, it_copy = itertools.tee(it)
    assert list(miter.unique(it)) == list(it_copy)


@hypothesis.given(st.text(string.ascii_lowercase))
def test_unique_with_key_function(s):
    # Confirm that when a sequence is concatenated with itself (subject to a key function),
    # the `miter.unique()` function returns the original, unique elements.
    hypothesis.assume(len(set(s)) == len(s))  # Ensure unique string.

    concat = "".join
    assert concat(miter.unique(s)) == s
    # Naturally, `s.lower()` is `s`.
    assert concat(miter.unique(s + s.lower(), key=str.lower)) == s
    assert concat(miter.unique(s + s.lower(), key=str.upper)) == s
    assert concat(miter.unique(s + s.upper(), key=str.lower)) == s
    assert concat(miter.unique(s + s.upper(), key=str.upper)) == s
