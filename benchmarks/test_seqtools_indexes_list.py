from __future__ import annotations

import itertools

import pytest

import miter


@pytest.fixture()
def sample_sequence():
    n_repeats = 1_000
    # Avoid small integers, which are interned by the Python interpreter.
    subsequence = range(1000, 2000)
    n = n_repeats * len(subsequence)
    return list(itertools.islice(itertools.cycle(subsequence), n))


def verify_result(seq, value, indexes):
    assert len(indexes) == sum(1 for elem in seq if elem == value)
    assert all(seq[i] == value for i in indexes)


def test_enumerate_filter(benchmark, sample_sequence):
    def indexes(seq, value):
        return [i for i, elem in enumerate(seq) if elem == value]

    value = sample_sequence[0]
    result = benchmark(indexes, sample_sequence, value)
    verify_result(sample_sequence, value, result)


def test_repeated_index(benchmark, sample_sequence):
    def indexes(seq, value):
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

    value = sample_sequence[0]
    result = benchmark(indexes, sample_sequence, value)
    verify_result(sample_sequence, value, result)


def test_miter_seqtools_indexes(benchmark, sample_sequence):
    def indexes(seq, value):
        return list(miter.seqtools.indexes(seq, value))

    value = sample_sequence[0]
    result = benchmark(indexes, sample_sequence, value)
    verify_result(sample_sequence, value, result)
