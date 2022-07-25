#include <algorithm>
#include <iostream>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

namespace py = pybind11;

namespace miter {

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

template <typename Key> class UniqueIterator {
  py::iterable iterable_;
  Key key_;
  py::iterator begin_;
  py::iterator end_;
  std::unordered_set<py::object, PyObjectHash, PyObjectEqual> unique_elements_;

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

using IdentityUniqueIterator = UniqueIterator<IdentityKey>;
using KeyFunctionUniqueIterator = UniqueIterator<CallableKey>;

py::object unique(py::iterable iterable, std::optional<py::function> key) {
  return key.has_value()
             ? py::cast(KeyFunctionUniqueIterator{iterable, CallableKey{*key}})
             : py::cast(IdentityUniqueIterator{iterable, IdentityKey{}});
};

} // namespace miter

PYBIND11_MODULE(_itertools, m) {
  using namespace pybind11::literals;

  py::class_<miter::IdentityUniqueIterator>(m, "IdentityUniqueIterator")
      .def("__iter__", &miter::IdentityUniqueIterator::iter)
      .def("__next__", &miter::IdentityUniqueIterator::next);

  py::class_<miter::KeyFunctionUniqueIterator>(m, "_KeyFunctionUniqueIterator")
      .def("__iter__", &miter::KeyFunctionUniqueIterator::iter)
      .def("__next__", &miter::KeyFunctionUniqueIterator::next);

  m.def("length", &miter::length, "iterable"_a,
        R"pbdoc(
Return the number of elements in ``iterable``.  This may be useful for un-sized iterables
(without a ``__len__`` function).
)pbdoc");

  m.def("all_equal", &miter::all_equal, "iterable"_a, R"pbdoc(
Return whether all elements of ``iterable`` are equal to each other.)pbdoc");

  m.def("unique", &miter::unique, "iterable"_a, "key"_a = std::nullopt,
        R"pbdoc(
Return an iterable over the unique elements in ``iterable``, according to ``key``, preserving order.
)pbdoc");
}
