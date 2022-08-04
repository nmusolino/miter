#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

#include "indexes.hpp"
#include "unique.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_miter, m) {
  using namespace pybind11::literals;

  m.def("length", &miter::length, "iterable"_a,
        R"pbdoc(
Return the number of elements in ``iterable``.  This may be useful for un-sized iterables
(without a ``__len__`` function).
)pbdoc");

  m.def("all_equal", &miter::all_equal, "iterable"_a, R"pbdoc(
Return whether all elements of ``iterable`` are equal to each other.)pbdoc");

  py::class_<miter::IdentityUniqueIterator>(m, "IdentityUniqueIterator")
      .def("__iter__", &miter::IdentityUniqueIterator::iter)
      .def("__next__", &miter::IdentityUniqueIterator::next);

  py::class_<miter::KeyFunctionUniqueIterator>(m, "_KeyFunctionUniqueIterator")
      .def("__iter__", &miter::KeyFunctionUniqueIterator::iter)
      .def("__next__", &miter::KeyFunctionUniqueIterator::next);

  m.def("unique", &miter::unique, "iterable"_a, "key"_a = std::nullopt,
        R"pbdoc(
Return an iterable over the unique elements in ``iterable``, according to ``key``, preserving order.
)pbdoc");

  m.def("all_unique", &miter::all_unique, "iterable"_a, "key"_a = std::nullopt,
        R"pbdoc(
Return whether all elements of ``iterable`` are unique (i.e. no two elements are equal).

If ``key`` is specified, it will be used to compare elements.
)pbdoc");

  py::class_<miter::SequenceIndexesIterator>(m, "_SequenceIndexesIterator")
      .def("__iter__", &miter::SequenceIndexesIterator::iter)
      .def("__next__", &miter::SequenceIndexesIterator::next);

  py::class_<miter::ListIndexesIterator>(m, "_ListIndexesIterator")
      .def("__iter__", &miter::ListIndexesIterator::iter)
      .def("__next__", &miter::ListIndexesIterator::next);

  py::class_<miter::TupleIndexesIterator>(m, "_TupleIndexesIterator")
      .def("__iter__", &miter::TupleIndexesIterator::iter)
      .def("__next__", &miter::TupleIndexesIterator::next);

  m.def("indexes", &miter::indexes, "sequence"_a, "value"_a,
        "start"_a = std::nullopt, "end"_a = std::nullopt,
        R"pbdoc(
Return an iterator over the indexes of all elements equal to ``value`` in ``sequence``.

If provided, the ``start`` and ``end`` parameters are interpreted as in slice notation
and are used to limit the search to a particular subsequence, as in the builtin
``list.index()`` method.)pbdoc");
}
