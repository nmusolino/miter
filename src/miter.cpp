#include <cstddef>

#include <algorithm> // std::min, std::max
#include <optional>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

namespace py = pybind11;

namespace miter {
namespace detail {

// Class that returns the Python-level hash of Python objects.
struct PyObjectHash {
  std::size_t operator()(const py::handle &obj) const { return py::hash(obj); }
};

// Class that compares Python objects using the Python equality operator.
struct PyObjectEqual {
  bool operator()(const py::handle &lhs, const py::handle &rhs) const {
    return lhs.equal(rhs);
  }
};

struct IdentityKey {
public:
  py::object operator()(const py::handle &obj) const {
    return py::reinterpret_borrow<py::object>(obj);
  }
};

struct CallableKey {
  py::function func_;

public:
  CallableKey(py::function func) : func_{func} {}

  py::object operator()(const py::handle &obj) const { return func_(obj); }
};

} // namespace detail

std::size_t length(py::iterable iterable) {
  if (py::isinstance<py::sequence>(iterable)) {
    py::sequence seq{iterable}; // Can we std::move?
    return seq.size();
  }
  return std::distance(iterable.begin(), iterable.end());
}

bool all_equal(py::iterable iterable) {
  auto it = std::begin(iterable);
  const auto end = std::end(iterable);
  if (it == end) {
    return true;
  }
  py::handle ref_value = *it;
  return std::all_of(
      it, end, [ref_value](const py::handle &h) { return h.equal(ref_value); });
}

template <typename Key> class UniqueIterator {
  py::iterable iterable_;
  Key key_;
  py::iterator begin_;
  py::iterator end_;
  std::unordered_set<py::object, detail::PyObjectHash, detail::PyObjectEqual>
      unique_elements_;

public:
  UniqueIterator(py::iterable it, Key key)
      : iterable_{it}, key_{std::move(key)}, begin_{std::begin(iterable_)},
        end_{std::end(iterable_)} {}

  UniqueIterator iter() const { return *this; }

  // Return next unique element.
  py::object next() {
    auto it = std::find_if(begin_, end_, [this](const py::handle &obj) {
      py::object key_result = key_(obj);
      auto [_, inserted] = unique_elements_.insert(key_result);
      return inserted;
    });
    if (it != end_) {
      return py::reinterpret_borrow<py::object>(*it);
    }
    throw py::stop_iteration{};
  }
};

using IdentityUniqueIterator = UniqueIterator<detail::IdentityKey>;
using KeyFunctionUniqueIterator = UniqueIterator<detail::CallableKey>;

py::object unique(py::iterable iterable, std::optional<py::function> key) {
  return key.has_value() ? py::cast(KeyFunctionUniqueIterator{iterable, *key})
                         : py::cast(IdentityUniqueIterator{iterable, {}});
};

template <typename It, typename Key>
bool all_unique_impl(It begin, It end, Key key) {
  std::unordered_set<py::object, detail::PyObjectHash, detail::PyObjectEqual>
      unique_elements;

  return std::all_of(begin, end, [&unique_elements, &key](const py::handle &h) {
    py::object key_result = key(h);
    auto [_, inserted] = unique_elements.insert(key_result);
    return inserted;
  });
}

bool all_unique(py::iterable iterable, std::optional<py::function> key) {
  // TODO(nmusolino): specialize for container-specific iterators.
  return key.has_value()
             ? all_unique_impl(std::begin(iterable), std::end(iterable),
                               detail::CallableKey{*key})
             : all_unique_impl(std::begin(iterable), std::end(iterable),
                               detail::IdentityKey{});
}

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
