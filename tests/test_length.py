from __future__ import annotations

import copy

import hypothesis
from hypothesis import strategies as st

import miter


def test_length():
    assert miter.length([]) == 0
    assert miter.length([0]) == 1
    assert miter.length([0] * 5) == 5
    assert miter.length("abcde") == 5
    # Test `miter.length()` with a non-sequence iterable.
    assert miter.length(i for i in range(100) if (i % 2 == 0)) == 50


def test_length_for_long_sequence():
    N = 1_000_000_000
    assert miter.length(range(N)) == N


@hypothesis.given(st.iterables(st.integers()))
def test_length_for_nonsequence(it):
    # Confirm that `miter.length()` returns the value obtained by an alternative approach.
    expected_length: int = sum(1 for _ in copy.deepcopy(it))  # Need to copy iterator.
    assert miter.length(it) == expected_length


@hypothesis.given(st.lists(st.integers()))
def test_length_for_sequence(seq):
    # Confirm that `miter.length()` returns the correct length of the sequence.
    assert miter.length(seq) == len(seq)
