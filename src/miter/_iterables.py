import typing
from typing import cast, Iterable, Sequence

import miter._core as _core
from miter._typing import Predicate

T = typing.TypeVar("T")

def count(iterable: Iterable) -> int:
    """
    Return the number of elements in `iterable`, by calling `len()` or
    by iterating and counting elements.

    Complexity: `O(1)` if `len(iterable)` succeeds, `O(N)` otherwise.
    """
    try:
        return len(cast(Sequence, iterable))
    except TypeError:
        pass
    return _core.count(iterable)

def count_if(iter: Iterable[T], pred: Predicate[T]) -> int:
    """
    Return the number of elements in `iterable` for which `pred`
    is true.

    Complexity: `O(N)` applications of the predicate function.
    """

    return _core.count(filter(pred, iter))
