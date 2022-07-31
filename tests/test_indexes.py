from __future__ import annotations

import array
import functools
import itertools
from typing import List

import hypothesis
import pytest
from hypothesis import strategies as st

import miter


def test_indexes_empty_sequence():
    assert list(miter.indexes([], 0)) == []


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
        pytest.param(functools.partial(array.array, "i"), id="array.array"),
        pytest.param(lambda _: _, id="range"),
    ],
)
def test_indexes_with_assorted_sequence_types(type_):
    seq = type_(range(10))
    assert list(miter.indexes(seq, -1)) == []
    assert list(miter.indexes(seq, 0)) == [0]
    assert list(miter.indexes(seq, 9)) == [9]
    assert list(miter.indexes(seq, 10)) == []


def test_indexes_with_long_sequence():
    seq = range(1_000_000)
    assert list(miter.indexes(seq, 5)) == [5]


@hypothesis.given(st.lists(st.integers(min_value=0, max_value=10)))
@hypothesis.settings(max_examples=200)
def test_indexes_properties(s: List[int]):
    # Property-based test that calls `miter.indexes()` and makes assertions about
    # the result.
    n: int = len(s)

    # Search for a value that is present in `s`, if possible.
    value = s[-1] if s else None

    ixs: List[int] = list(miter.indexes(s, value))

    assert sorted(ixs) == ixs, "Expected sorted indexes."
    assert len(set(ixs)) == len(ixs), "Expected unique indexes."

    # Elements at every returned index should equal `value`.
    for i in ixs:
        assert s[i] == value

    # Elements at every *other* valid index should not equal `value`.
    ixs_complement: List[int] = sorted(set(range(n)) - set(ixs))
    for i in ixs_complement:
        assert s[i] != value


def test_indexes_with_start():
    seq = [3, 4, 5, 6]
    for value, start in itertools.product(seq, range(len(seq))):
        try:
            expected = seq.index(value, start)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(miter.indexes(seq, value)) == [expected]
        else:
            assert list(miter.indexes(seq, value, start=start)) == []


def test_indexes_with_end():
    seq = [3, 4, 5, 6]
    for value, end in itertools.product(seq, range(len(seq))):
        try:
            expected = seq.index(value, 0, end)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(miter.indexes(seq, value)) == [expected]
        else:
            assert list(miter.indexes(seq, value, end=end)) == []


def test_indexes_with_start_end():
    seq = [3, 4, 5, 6]
    n = len(seq)
    for value, start, end in itertools.product(seq, range(-n, n), range(-n, n)):
        try:
            expected = seq.index(value, start, end)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(miter.indexes(seq, value, start, end)) == [expected]
        else:
            assert list(miter.indexes(seq, value, start, end)) == []


def test_indexes_non_sequence():
    nonseq = set(range(5))
    with pytest.raises(TypeError):
        miter.indexes(nonseq, 0)
