import typing
from typing import Callable, TypeAlias

V = typing.TypeVar("V")

# Predicate[T] is a logical predicate function, operating on `T`.
Predicate: TypeAlias = Callable[[V], bool]
