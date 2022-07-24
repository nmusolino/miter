from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Optional, TypeVar

T = TypeVar("T")

def indexes(
    seq: Sequence[T], value: T, start: Optional[int], end: Optional[int]
) -> Iterable[int]: ...
