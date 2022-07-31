from __future__ import annotations

import itertools

import hypothesis
from hypothesis import strategies as st


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


element_type_strategy = st.booleans() | st.characters() | st.integers() | st.tuples(st.integers())

@hypothesis.given(st.iterables(element_type_strategy, unique=True))
def test_all_unique_for_unique_iterable(it):
    assert miter.all_unique(it)


@hypothesis.given(st.iterables(element_type_strategy, min_size=1))
def test_all_unique_for_nonunique_iterable(it):
    first = next(it)

    nonunique_iterable = itertools.chain([first], it, [first])
    assert not miter.all_unique(nonunique_iterable)
