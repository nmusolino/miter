from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Callable, Hashable, Optional, TypeVar

T = TypeVar("T")

def length(iterable: Iterable[T]) -> int: ...
def all_equal(iterable: Iterable[T]) -> bool: ...
def unique(
    iterable: Iterable[T], key: Optional[Callable[[T], Hashable]] = None
) -> Iterable[T]: ...
def indexes(
    seq: Sequence[T], value: T, start: Optional[int], end: Optional[int]
) -> Iterable[int]: ...
