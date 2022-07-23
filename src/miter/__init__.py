"""
Copyright (c) 2022 Nicholas Musolino. All rights reserved.

miter: Python utility library for iterables and sequences
"""
from __future__ import annotations

import enum as _enum
from functools import lru_cache
from typing import Optional

from ._version import version as __version__

__all__ = ("__version__",)


class ImplPreference(_enum.Enum):
    """Enum of implementation preferences."""

    PREFER_CPP = 0
    REQUIRE_PYTHON = 1
    REQUIRE_CPP = 2


class ImplResolution(_enum.Enum):
    """Enum indicating a selected implementation."""

    PYTHON = 1
    CPP = 2


@lru_cache()
def _get_impl_preference(override: Optional[str] = None) -> ImplPreference:
    """Return the implementation preference from the 'MITER_IMPLEMENTATION' environment variable.
    To allow testing, if `override` is provided, its value is used instead.

    Examples:
    >>> _get_impl_preference("")
    <ImplPreference.PREFER_CPP: 0>
    >>> _get_impl_preference("require_python")
    <ImplPreference.REQUIRE_PYTHON: 1>
    >>> _get_impl_preference("bad_choice")
    Traceback (most recent call last):
    ...
    ValueError: Invalid MITER_IMPLEMENTATION value: 'bad_choice'. Valid values are: PREFER_CPP, REQUIRE_PYTHON, REQUIRE_CPP
    """
    import os

    value: Optional[str] = override or os.environ.get("MITER_IMPLEMENTATION")
    if value is None:
        return ImplPreference.PREFER_CPP  # Default

    try:
        return ImplPreference[value.upper()]
    except KeyError:
        valid_values = ", ".join(pref.name for pref in ImplPreference)
        raise ValueError(
            f"Invalid MITER_IMPLEMENTATION value: {value!r}. Valid values are: {valid_values}"
        )


def is_cpp_impl_available() -> bool:
    """Return whether C++ extension implementations are available for all `miter` modules."""
    try:
        import miter._seqtools  # noqa: F401

        return True
    except ImportError:
        return False


@lru_cache()
def resolved_implementation(pref: Optional[ImplPreference] = None) -> ImplResolution:
    """Return the implementation corresponding to `pref`."""
    resolutions = {
        ImplPreference.PREFER_CPP: (
            ImplResolution.CPP if is_cpp_impl_available() else ImplResolution.PYTHON
        ),
        ImplPreference.REQUIRE_PYTHON: ImplResolution.PYTHON,
        ImplPreference.REQUIRE_CPP: ImplResolution.CPP,
    }
    # The following lookup should always succeed, since `resolutions` contains all
    # enum values.
    assert set(resolutions.keys()) == set(ImplPreference)
    return resolutions[pref or _get_impl_preference()]
