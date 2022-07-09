from __future__ import annotations

import array
import functools
import itertools

import pytest

from miter import seqtools


def test_indexes_empty_sequence():
    assert list(seqtools.indexes([], 0)) == []


def test_indexes_simple_sequence():
    assert list(seqtools.indexes("abc", "a")) == [0]
    assert list(seqtools.indexes("abc", "b")) == [1]
    assert list(seqtools.indexes("abc", "c")) == [2]
    assert list(seqtools.indexes("abc", "d")) == []
    assert list(seqtools.indexes("abca", "a")) == [0, 3]
    assert list(seqtools.indexes("abracadabra", "a")) == [0, 3, 5, 7, 10]


def test_indexes_incongruous_value():
    assert list(seqtools.indexes("abc", 0)) == []
    assert list(seqtools.indexes(range(5), "a")) == []


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
    assert list(seqtools.indexes(seq, -1)) == []
    assert list(seqtools.indexes(seq, 0)) == [0]
    assert list(seqtools.indexes(seq, 9)) == [9]
    assert list(seqtools.indexes(seq, 10)) == []


def test_indexes_with_long_sequence():
    seq = range(1_000_000)
    assert list(seqtools.indexes(seq, 5)) == [5]


def test_indexes_with_start():
    seq = [3, 4, 5, 6]
    assert list(seqtools.indexes(seq, 4, start=0)) == [1]
    assert list(seqtools.indexes(seq, 4, start=1)) == [1]
    assert list(seqtools.indexes(seq, 4, start=2)) == []
    assert list(seqtools.indexes(seq, 4, start=3)) == []
    assert list(seqtools.indexes(seq, 4, start=4)) == []


def test_indexes_with_start_systematic():
    seq = [3, 4, 5, 6]
    for value, start in itertools.product(seq, range(len(seq))):
        try:
            expected = seq.index(value, start)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(seqtools.indexes(seq, value)) == [expected]
        else:
            assert list(seqtools.indexes(seq, value, start=start)) == []


def test_indexes_with_end():
    seq = [3, 4, 5, 6]
    for value, end in itertools.product(seq, range(len(seq))):
        try:
            expected = seq.index(value, 0, end)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(seqtools.indexes(seq, value)) == [expected]
        else:
            assert list(seqtools.indexes(seq, value, end=end)) == []


def test_indexes_with_start_end():
    seq = [3, 4, 5, 6]
    n = len(seq)
    for value, start, end in itertools.product(seq, range(-n, n), range(-n, n)):
        try:
            expected = seq.index(value, start, end)
        except ValueError:
            expected = None

        if expected is not None:
            assert list(seqtools.indexes(seq, value, start, end)) == [expected]
        else:
            assert list(seqtools.indexes(seq, value, start, end)) == []


def test_indexes_non_sequence():
    nonseq = set(range(5))
    with pytest.raises(TypeError):
        seqtools.indexes(nonseq, 0)
