from __future__ import annotations

import array
import collections
import functools
import itertools
from typing import List

import hypothesis
import pytest
from hypothesis import strategies as st

import miter


def is_unique(coll: collections.abc.Collection) -> bool:
    """Return whether the elements of ``coll`` are unique."""
    return len(set(coll)) == len(coll)


def test_indexes_empty_sequence():
    assert list(miter.indexes([], 0)) == []


def test_indexes_non_sequence():
    nonseq = set(range(5))
    with pytest.raises(TypeError):
        miter.indexes(nonseq, 0)


def test_indexes_simple_sequence():
    assert list(miter.indexes("abc", "a")) == [0]
    assert list(miter.indexes("abc", "b")) == [1]
    assert list(miter.indexes("abc", "c")) == [2]
    assert list(miter.indexes("abc", "d")) == []
    assert list(miter.indexes("abca", "a")) == [0, 3]
    assert list(miter.indexes("abracadabra", "a")) == [0, 3, 5, 7, 10]


def test_indexes_incongruous_value():
    assert list(miter.indexes("abc", 0)) == []
    assert list(miter.indexes(range(5), "a")) == []


@pytest.mark.parametrize(
    "type_",
    [
        tuple,
        list,
        bytes,
        pytest.param(functools.partial(array.array, "i"), id="array.array"),
        pytest.param(lambda _: _, id="range"),
    ],
)
def test_indexes_with_assorted_sequence_types(type_):
    seq = type_(range(1, 10))
    assert list(miter.indexes(seq, 0)) == []
    assert list(miter.indexes(seq, 1)) == [0]
    assert list(miter.indexes(seq, 9)) == [8]
    assert list(miter.indexes(seq, 10)) == []


def test_indexes_with_long_sequence():
    seq = range(1_000_000)
    assert list(miter.indexes(seq, 5)) == [5]


def test_indexes_bytes():
    seq = b"abcde"

    # Test with length-1 bytes argument for `value`.
    value = seq[2:3]
    assert isinstance(value, bytes) and len(value) == 1
    assert list(miter.indexes(seq, value)) == [seq.index(value)]

    # Test with length-2 bytes argument for `value`.
    value = seq[2:4]
    assert isinstance(value, bytes) and len(value) == 2
    assert list(miter.indexes(seq, value)) == [seq.index(value)]

    # Test with integer argument for `value`.
    value = seq[2]
    assert isinstance(value, int)
    assert list(miter.indexes(seq, value)) == [2]

    assert list(miter.indexes(seq, 0xFF)) == []

    with pytest.raises(ValueError):
        miter.indexes(seq, -1)
    with pytest.raises(ValueError):
        miter.indexes(seq, 0x100)

    # When called with a type other than bytes or int, a TypeError is raised.
    with pytest.raises(TypeError):
        miter.indexes(seq, "")


@hypothesis.given(st.lists(st.integers(min_value=0, max_value=10)))
@hypothesis.settings(max_examples=200)
def test_indexes_properties(seq: List[int]):
    hypothesis.assume(seq)
    # Property-based test that calls `miter.indexes()` and makes assertions about
    # the result.
    n: int = len(seq)

    # Search for the most common element in `s`, if possible.
    [(value, _)] = collections.Counter(seq).most_common(1)

    ixs: List[int] = list(miter.indexes(seq, value))

    assert sorted(ixs) == ixs, "Expected sorted indexes."
    assert is_unique(ixs), "Expected unique indexes."

    # Elements at every returned index should equal `value`.
    for i in ixs:
        assert seq[i] == value

    # Elements at every *other* valid index should not equal `value`.
    ixs_complement: List[int] = sorted(set(range(n)) - set(ixs))
    for i in ixs_complement:
        assert seq[i] != value


@hypothesis.given(st.lists(st.integers(), unique=True))
def test_indexes_with_start(seq):
    # For a unique list, the result returned by `miter.indexes()` should
    # match the result from the builtin `list.index()` method.
    assert is_unique(seq), "Expected unique sequence based on hypothesis strategy."

    for value, start in itertools.product(seq, range(len(seq))):
        try:
            expected_ixs = [seq.index(value, start)]
        except ValueError:
            expected_ixs = []  # No indexes.

        assert list(miter.indexes(seq, value, start=start)) == expected_ixs


@hypothesis.given(st.lists(st.integers(), unique=True))
def test_indexes_with_end(seq):
    # For a unique list, the result returned by `miter.indexes()` should
    # match the result from the builtin `list.index()` method.
    assert is_unique(seq), "Expected unique sequence from hypothesis strategy."

    for value, end in itertools.product(seq, range(len(seq))):
        try:
            expected_ixs = [seq.index(value, 0, end)]
        except ValueError:
            expected_ixs = []

        assert list(miter.indexes(seq, value, end=end)) == expected_ixs


# Each example requires O(N^3) iterations within the test, so restrict list size.
@hypothesis.given(st.lists(st.integers(), max_size=10, unique=True))
@hypothesis.settings(max_examples=50)
def test_indexes_with_start_end(seq):
    # For a unique list, the result returned by `miter.indexes()` should
    # match the result from the builtin `list.index()` method.
    assert is_unique(seq), "Expected unique sequence from hypothesis strategy."

    n = len(seq)
    for value, start, end in itertools.product(seq, range(-n, n), range(-n, n)):
        try:
            expected_ixs = [seq.index(value, start, end)]
        except ValueError:
            expected_ixs = []

        assert list(miter.indexes(seq, value, start=start, end=end)) == expected_ixs
