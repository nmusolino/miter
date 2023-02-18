#include <cstddef>

#include <algorithm> // std::min, std::max
#include <optional>
#include <string_view>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // for std::optional

namespace py = pybind11;

namespace miter {
namespace {
// Normalize or fix-up the index of `seq` so that it is a valid index, OR a
// past-the-end iterator.
//
// The list.index() method does not raise when the user-supplied values of
// `start` or `end` are incorrect, but instead tries to do what the user means.
// This function does the same sort of thing.
py::ssize_t normalize_index(const py::ssize_t seq_length, py::ssize_t index) {
  if (index < 0) {
    index += seq_length;
  }
  return std::clamp(py::ssize_t{0}, index, seq_length);
}

ssize_t size(const py::bytes &b) { return PyBytes_GET_SIZE(b.ptr()); }

const char *begin(const py::bytes &b) { return PyBytes_AS_STRING(b.ptr()); }

const char *end(const py::bytes &b) { return begin(b) + size(b); }

} // namespace

// Class for searching for a single character in `str` or `bytes`.
template <typename ObjectType, typename CharType>
class CharacterIndexesIterator {
  ObjectType seq_;
  const CharType *const begin_;
  const CharType *curr_;
  const CharType *const end_;
  py::object value_;
  const CharType value_char_;

public:
  CharacterIndexesIterator(ObjectType seq, py::object value,
                           CharType value_char, size_t start_index,
                           size_t end_index)
      : seq_{seq}, begin_{miter::begin(seq)}, curr_{begin_ + start_index},
        end_{begin_ + end_index}, value_{value}, value_char_{value_char} {}

  CharacterIndexesIterator iter() const { return *this; }

  size_t next() {
    curr_ = std::find(curr_, end_, value_char_);
    if (curr_ != end_) {
      return curr_++ - begin_;
    }
    throw py::stop_iteration{};
  }
};

// Class for searching for a character sequence in `str` or `bytes`.
template <typename ObjectType, typename CharType>
class SubstringIndexesIterator {
  ObjectType seq_;
  const CharType *const begin_;
  const CharType *curr_;
  const CharType *const end_;
  ObjectType value_;
  const CharType *const value_begin_;
  const CharType *const value_end_;

public:
  SubstringIndexesIterator(ObjectType seq, ObjectType value, size_t start_index,
                           size_t end_index)
      : seq_{seq}, begin_{miter::begin(seq)}, curr_{begin_ + start_index},
        end_{begin_ + end_index}, value_{value},
        value_begin_{miter::begin(value)}, value_end_{miter::end(value)} {}

  SubstringIndexesIterator iter() const { return *this; }

  size_t next() {
    // TODO(nmusolino): use std::boyer_moore_horspool_searcher.
    curr_ = std::search(curr_, end_, value_begin_, value_end_);
    if (curr_ != end_) {
      return curr_++ - begin_;
    }
    throw py::stop_iteration{};
  }
};

// OVERLOADS FOR py::bytes
SubstringIndexesIterator<py::bytes, char>
indexes(py::bytes seq, py::bytes value, std::optional<py::ssize_t> start,
        std::optional<py::ssize_t> end) {
  const auto seq_size = miter::size(seq);
  const size_t start_ix = normalize_index(seq_size, start.value_or(0));
  const size_t end_ix = normalize_index(seq_size, end.value_or(seq_size));
  return {seq, value, start_ix, end_ix};
}

CharacterIndexesIterator<py::bytes, char>
indexes(py::bytes seq, py::int_ value, std::optional<py::ssize_t> start,
        std::optional<py::ssize_t> end) {
  const auto seq_size = miter::size(seq);
  const size_t start_ix = normalize_index(seq_size, start.value_or(0));
  const size_t end_ix = normalize_index(seq_size, end.value_or(seq_size));

  // A Python `int` could overflow `long long`; this is not handled.
  const long long val = value.operator long long();
  if (!(0 <= val && val < 256)) {
    throw py::value_error{"byte must be in range(0, 256): " +
                          std::to_string(val)};
  }
  return {seq, value, static_cast<char>(val), start_ix, end_ix};
}

py::object indexes(py::bytes, py::object value,
                   std::optional<py::ssize_t> start,
                   std::optional<py::ssize_t> end) {
  const py::type value_type = py::type::of(value);
  std::string value_type_name =
      py::str(static_cast<const py::handle &>(value_type));
  throw py::type_error{
      "`value` argument should be integer or bytes-like object, not " +
      value_type_name};
}

template <typename SequenceType>
using SequenceIterator = decltype(std::declval<SequenceType>().begin());

template <typename SequenceType> class IndexesIterator {
  using Iterator = SequenceIterator<SequenceType>;

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

ListIndexesIterator indexes(py::list seq, py::object value,
                            std::optional<py::ssize_t> start,
                            std::optional<py::ssize_t> end) {
  const size_t start_ix = normalize_index(seq.size(), start.value_or(0));
  const size_t end_ix = normalize_index(seq.size(), end.value_or(seq.size()));
  return {seq, value, start_ix, end_ix};
}

TupleIndexesIterator indexes(py::tuple seq, py::object value,
                             std::optional<py::ssize_t> start,
                             std::optional<py::ssize_t> end) {
  const size_t start_ix = normalize_index(seq.size(), start.value_or(0));
  const size_t end_ix = normalize_index(seq.size(), end.value_or(seq.size()));
  return {seq, value, start_ix, end_ix};
}

// Generic sequence overload.
SequenceIndexesIterator indexes(py::sequence seq, py::object value,
                                std::optional<py::ssize_t> start,
                                std::optional<py::ssize_t> end) {
  const size_t start_ix = normalize_index(seq.size(), start.value_or(0));
  const size_t end_ix = normalize_index(seq.size(), end.value_or(seq.size()));
  return {seq, value, start_ix, end_ix};
}

namespace {

template <typename T>
void bind_iterator_class(py::module_ m, std::string_view name) {
  py::class_<T>(m, name.data())
      .def("__iter__", &T::iter)
      .def("__next__", &T::next);
}

} // namespace

void init_indexes(py::module_ m) {
  using namespace pybind11::literals; // For literal suffix `_a`.

  bind_iterator_class<miter::CharacterIndexesIterator<py::bytes, char>>(
      m, "_BytesCharacterIndexesIterator");
  bind_iterator_class<miter::SubstringIndexesIterator<py::bytes, char>>(
      m, "_BytesSubstringIndexesIterator");
  bind_iterator_class<miter::SequenceIndexesIterator>(
      m, "_SequenceIndexesIterator");
  bind_iterator_class<miter::ListIndexesIterator>(m, "_ListIndexesIterator");
  bind_iterator_class<miter::TupleIndexesIterator>(m, "_TupleIndexesIterator");

  // TODO(nmusolino): can we add a docstring that applies to the entire
  // overload?
  m.def("indexes",
        py::overload_cast<py::bytes, py::int_, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt);

  m.def("indexes",
        py::overload_cast<py::bytes, py::bytes, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt);

  m.def("indexes",
        py::overload_cast<py::bytes, py::object, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt);

  m.def("indexes",
        py::overload_cast<py::list, py::object, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt);

  m.def("indexes",
        py::overload_cast<py::tuple, py::object, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt);

  // Generic sequence overload.
  m.def("indexes",
        py::overload_cast<py::sequence, py::object, std::optional<py::ssize_t>,
                          std::optional<py::ssize_t>>(&miter::indexes),
        "sequence"_a, "value"_a, "start"_a = std::nullopt,
        "end"_a = std::nullopt,
        R"pbdoc(
Return an iterator over the indexes of all elements equal to ``value`` in ``sequence``.

If provided, the ``start`` and ``end`` parameters are interpreted as in slice notation
and are used to limit the search to a particular subsequence, as in the builtin
``list.index()`` method.)pbdoc");
}

} // namespace miter
