#pragma once

#include <cstddef>

#include <algorithm> // std::min, std::max
#include <optional>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

namespace py = pybind11;

namespace miter {
namespace detail {

// Normalize or fix-up the index of `seq` so that it is a valid index.
//
// The list.index() method does not raise when the user-supplied values of
// `start` or `end` are incorrect, but instead tries to do what the user means.
// This function does the same sort of thing.
size_t normalize_index(const py::sequence &seq, py::ssize_t index) {
  const auto seq_len = static_cast<py::ssize_t>(seq.size());
  if (index >= 0) {
    return std::min(index, seq_len);
  } else {
    return std::max(py::ssize_t{0}, seq_len + index);
  }
}

template <typename SequenceType>
using SequenceIterator = decltype(std::declval<SequenceType>().begin());

} // namespace detail

template <typename SequenceType> class IndexesIterator {
  using Iterator = detail::SequenceIterator<SequenceType>;

  SequenceType seq_;
  const py::object value_;
  const Iterator begin_;
  Iterator curr_;
  const Iterator end_;

public:
  IndexesIterator(SequenceType seq, py::object value, size_t start_index,
                  size_t end_index)
      : seq_{seq}, value_{value}, begin_{seq.begin()},
        curr_{begin_ + start_index}, end_{begin_ + end_index} {}

  IndexesIterator(SequenceType seq, py::object value)
      : IndexesIterator{seq, value, /*begin_index*/ 0, /*end_index*/ 0} {}

  IndexesIterator iter() const { return *this; }

  size_t next() {
    if (curr_ < end_) {
      const auto found = curr_ =
          std::find_if(curr_, end_, [this](const auto &elem) {
            PyObject *ptr = elem.ptr();
            return value_.equal(py::handle{ptr});
          });
      curr_++;
      if (found != end_) {
        return found - begin_;
      }
    }
    throw py::stop_iteration{};
  }
};

using SequenceIndexesIterator = IndexesIterator<py::sequence>;
using ListIndexesIterator = IndexesIterator<py::list>;
using TupleIndexesIterator = IndexesIterator<py::tuple>;

py::object indexes(py::sequence seq, py::object value,
                   std::optional<py::ssize_t> start,
                   std::optional<py::ssize_t> end) {
  const size_t start_index = detail::normalize_index(seq, start.value_or(0));
  const size_t end_index =
      detail::normalize_index(seq, end.value_or(seq.size()));
  if (py::isinstance<py::list>(seq)) {
    return py::cast(
        ListIndexesIterator(py::list{seq}, value, start_index, end_index));
  }
  if (py::isinstance<py::tuple>(seq)) {
    return py::cast(
        TupleIndexesIterator(py::list{seq}, value, start_index, end_index));
  }
  return py::cast(SequenceIndexesIterator{seq, value, start_index, end_index});
}

} // namespace miter
