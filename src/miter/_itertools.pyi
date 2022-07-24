from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")

def length(iterable: Iterable[T]) -> int: ...
