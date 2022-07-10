from __future__ import annotations

import functools
import itertools
import string

import pytest

import miter.seqtools


@functools.cache
def sample_sequence(type_, n):
    """Return a sample sequence of the given `type` and length `n`."""
    subsequence = string.ascii_letters if (type_ is str) else range(50)
    return type_(itertools.islice(itertools.cycle(subsequence), n))


def indexes_filtered_enumerate(seq, value):
    return [i for i, elem in enumerate(seq) if elem == value]


def indexes_repeated_index(seq, value):
    def index_generator():
        i = 0
        try:
            while True:
                i = seq.index(value, i)
                yield i
                i += 1
        except ValueError:
            pass

    return list(index_generator())


@pytest.mark.parametrize(
    "indexes_impl",
    [
        indexes_filtered_enumerate,
        indexes_repeated_index,
        pytest.param(miter.seqtools.indexes, id="miter.seqtools.indexes"),
    ],
)
@pytest.mark.parametrize("seq_type", [list, tuple, str, bytes])
def test_indexes(benchmark, seq_type, indexes_impl):
    n = 32 * 1024
    seq = sample_sequence(seq_type, n)
    assert isinstance(seq, seq_type)

    value = seq[0]
    result = benchmark(indexes_filtered_enumerate, seq, value)

    assert all(seq[i] == value for i in result)
    assert len(result) == sum(int(elem == value) for elem in seq)
