import typing
from typing import cast, Sequence, Iterable

from miter import _core
from miter._typing import Predicate

T = typing.TypeVar("T")

def count(iterable: Iterable) -> int:
    try:
        return len(cast(Sequence, iterable))
    except TypeError:
        pass
    return _core.count(iterable)

def count_if(iter: Iterable[T], pred: Predicate[T]) -> int:
    return _core.count(filter(pred, iter))
