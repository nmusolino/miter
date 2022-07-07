from __future__ import annotations

import array
import functools

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


def test_long_sequence():
    seq = range(1_000_000)
    assert list(seqtools.indexes(seq, 5)) == [5]


# TODO(nmusolino): start, end test
# TODO(nmusolino): negative start, end test
# TODO(nmusolino): bad start test
# TODO(nmusolino): bad end test
# TODO(nmusolino): non-sequence test
