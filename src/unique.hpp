#pragma once

#include <algorithm> // std::min, std::max
#include <optional>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

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
} // namespace miter
