#include <string>

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

namespace nb = nanobind;

std::string hello_from_bin() { return "Hello from miter!"; }

NB_MODULE(_core, m) {
  using namespace nb::literals;

  m.doc() = "nanobind hello module";

  m.def("hello_from_bin", &hello_from_bin, R"pbdoc(
      A function that returns a Hello string.
  )pbdoc");
}
