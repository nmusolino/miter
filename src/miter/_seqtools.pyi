from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import TypeVar

T = TypeVar("T")  # Can be anything

def indexes(seq: Sequence[T], value: T, start: int, end: int) -> Iterable[int]: ...