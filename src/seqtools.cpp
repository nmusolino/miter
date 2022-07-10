#include <cstddef>

#include <algorithm> // std::min, std::max
#include <optional>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

namespace py = pybind11;

namespace miter {

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

class IndexesIterator {
private:
  // TODO(nmusolino): add alternative using fast iterator in pybind11
  // TODO(nmusolino): can we cache end_ index, or could sequence change during
  // iteration?
  py::sequence seq_;
  py::object value_;
  size_t start_ = {};
  size_t end_ = {};

public:
  IndexesIterator(py::sequence seq, py::object value, size_t start, size_t end)
      : seq_{seq}, value_{value}, start_{start}, end_{end} {}

  IndexesIterator(py::sequence seq, py::object value)
      : IndexesIterator{seq, value, /*start*/ 0, /*end*/ seq.size()} {}

  IndexesIterator iter() { return *this; }
  size_t next() {
    while (start_ < end_) {
      const auto idx = start_++;
      assert(0 <= idx && idx < seq_.size());
      const py::object &elem = seq_[idx];
      if (elem.equal(value_)) {
        return idx;
      }
    }
    assert(start_ <= end_);
    throw py::stop_iteration{};
  }
};

// Iterator over indexes for a "fast" sequence, i.e. that
//
class ListTupleIndexesIterator {
  using sequence_iterator = py::detail::list_iterator; // Also works for tuple
private:
  const py::sequence seq_;
  const py::object value_;
  const sequence_iterator begin_;
  sequence_iterator it_;
  const sequence_iterator end_;

public:
  ListTupleIndexesIterator(py::list seq, py::object value, size_t start_index,
                           size_t end_index)
      : seq_{seq}, value_{value}, begin_{seq.begin()},
        it_{begin_ + start_index}, end_{begin_ + end_index} {}

  ListTupleIndexesIterator(py::tuple seq, py::object value, size_t start_index,
                           size_t end_index)
      : seq_{seq}, value_{value}, begin_{seq.begin()},
        it_{begin_ + start_index}, end_{begin_ + end_index} {}

  ListTupleIndexesIterator iter() { return *this; }

  size_t next() {
    while (it_ < end_) {
      const auto result = it_ = std::find_if(
          it_, end_, [this](const py::handle &h) { return h.equal(value_); });
      if (it_ == end_) {
        break;
      }
      it_++;
      assert((*result).equal(value_));
      return result - begin_;
    }
    throw py::stop_iteration{};
  }
};

IndexesIterator indexes(py::sequence seq, py::object value,
                        std::optional<py::ssize_t> start,
                        std::optional<py::ssize_t> end) {
  const size_t start_index = normalize_index(seq, start.value_or(0));
  const size_t end_index = normalize_index(seq, end.value_or(seq.size()));
  return IndexesIterator{seq, value, start_index, end_index};
}

ListTupleIndexesIterator list_indexes(py::list seq, py::object value,
                                      std::optional<py::ssize_t> start,
                                      std::optional<py::ssize_t> end) {
  const size_t start_index = normalize_index(seq, start.value_or(0));
  const size_t end_index = normalize_index(seq, end.value_or(seq.size()));
  return ListTupleIndexesIterator{seq, value, start_index, end_index};
}

ListTupleIndexesIterator tuple_indexes(py::tuple seq, py::object value,
                                       std::optional<py::ssize_t> start,
                                       std::optional<py::ssize_t> end) {
  const size_t start_index = normalize_index(seq, start.value_or(0));
  const size_t end_index = normalize_index(seq, end.value_or(seq.size()));
  return ListTupleIndexesIterator{seq, value, start_index, end_index};
}

} // namespace miter

PYBIND11_MODULE(_seqtools, m) {
  using namespace pybind11::literals;

  constexpr auto indexes_doc = R"pbdoc(
Return an iterator over the indexes of all elements equal to ``value`` in ``sequence``.

If provided, the ``start`` and ``end`` parameters are interpreted as in slice notation
and are used to limit the search to a particular subsequence, as in the builtin
``list.index()`` method.)pbdoc";

  py::class_<miter::IndexesIterator>(m, "_IndexesIterator")
      .def("__iter__", &miter::IndexesIterator::iter)
      .def("__next__", &miter::IndexesIterator::next);

  py::class_<miter::ListTupleIndexesIterator>(m, "_ListTupleIndexesIterator")
      .def("__iter__", &miter::ListTupleIndexesIterator::iter)
      .def("__next__", &miter::ListTupleIndexesIterator::next);

  m.def("indexes", &miter::list_indexes, "sequence"_a, "value"_a,
        "start"_a = std::nullopt, "end"_a = std::nullopt, indexes_doc);
  m.def("indexes", &miter::tuple_indexes, "sequence"_a, "value"_a,
        "start"_a = std::nullopt, "end"_a = std::nullopt, indexes_doc);
  m.def("indexes", &miter::indexes, "sequence"_a, "value"_a,
        "start"_a = std::nullopt, "end"_a = std::nullopt, indexes_doc);
}
