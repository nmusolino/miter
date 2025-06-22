#include <string>
#include <cstdint>

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>

namespace nb = nanobind;


std::int64_t count(nb::iterable iter) {
    std::int64_t count = 0;
    // difference_type not available for nanobind iterator.
    for (auto it = iter.begin(), end = iter.end(); it != end; ++it) {
        ++count;
    }
    return count;
}




NB_MODULE(_core, m) {
  using namespace nb::literals;

  m.doc() = "nanobind hello module";

  m.def("count", &count, nb::arg("iterable"), R"pbdoc(
      Return the number of elements in the iterable.
  )pbdoc");

}
