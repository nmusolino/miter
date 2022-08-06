#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace miter {

// init_* functions defined in other .cpp files.
void init_indexes(py::module_ m);
void init_unique(py::module_ m);

} // namespace miter

PYBIND11_MODULE(_miter, m) {
  miter::init_indexes(m);
  miter::init_unique(m);
}
