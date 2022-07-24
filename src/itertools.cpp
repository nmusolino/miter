#include <algorithm>
#include <iostream>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace miter {

// Normalize or fix-up the i

void consume(py::iterable iterable) {}

std::size_t length(py::iterable iterable) {
  if (py::isinstance<py::sequence>(iterable)) {
    py::sequence seq{iterable}; // Can we std::move?
    std::cout << "Using sequence case; length " << seq.size() << std::endl;
    return seq.size();
  }
  return std::distance(iterable.begin(), iterable.end());
}

} // namespace miter

PYBIND11_MODULE(_itertools, m) {
  using namespace pybind11::literals;

  m.def("length", &miter::length, "iterable"_a,
        R"pbdoc(
Return the number of elements in ``iterable``.  This may be useful for un-sized iterables
(without a ``__len__`` function).
)pbdoc");
}
