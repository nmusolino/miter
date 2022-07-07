#include <pybind11/pybind11.h>

#include <iostream>

namespace py = pybind11;

namespace miter {

// TODO(nmusolino): add alternative using fast iterator in pybind11
class IndexesRange {
private:
  // TODO(nmusolino): can we cache end_ index, or could sequence change during
  // iteration?
  py::sequence seq_;
  py::object value_;
  size_t start_ = {};
  size_t end_ = {};

public:
  IndexesRange(py::sequence seq, py::object value, size_t start, size_t end)
      : seq_{seq}, value_{value}, start_{start}, end_{seq.size()} {}

  IndexesRange(py::sequence seq, py::object value)
      : IndexesRange{seq, value, /*start*/ 0, /*end*/ seq.size()} {}

  IndexesRange iter() { return *this; }
  size_t next() {
    while (start_ != end_) {
      const auto idx = start_++;
      const py::object &elem = seq_[idx];
      if (elem.equal(value_)) {
        return idx;
      }
    }
    assert(start_ == end_);
    throw py::stop_iteration{};
  }
};

IndexesRange indexes(py::sequence seq, py::object value, ssize_t start,
                     ssize_t end) {
  // TODO(nmusolino): convert potentially negative index to positive index.
  return IndexesRange{seq, value, static_cast<size_t>(start),
                      static_cast<size_t>(end)};
}

} // namespace miter

PYBIND11_MODULE(_seqtools, m) {
  m.doc() = R"pbdoc(
      Miter seqtools module
      -----------------------
      .. currentmodule:: miter.seqtools
      .. autosummary::
         :toctree: _generate
         add
         subtract
  )pbdoc";

  using namespace pybind11::literals;

  py::class_<miter::IndexesRange>(m, "_IndexesRange")
      .def("__iter__", &miter::IndexesRange::iter)
      .def("__next__", &miter::IndexesRange::next);

  m.def("indexes", &miter::indexes, "sequence"_a, "value"_a,
        "start"_a = ssize_t{0}, "end"_a = ssize_t{0},
        R"pbdoc(Return all indexes of `value` in `sequence`.)pbdoc");
}
