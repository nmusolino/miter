Miter Package Documentation
===========================

The ``miter`` package provides utility functions for iterables and sequences in Python,
with an emphasis on correctness and performance.

Core functionality is implemented in C++ within an extension module, with pure Python
versions of functions present as a fallback if the extension module cannot be built.

The ``miter`` package was inspired by the
`toolz <https://toolz.readthedocs.io/en/latest/>`__ package and by the
`itertools <https://docs.python.org/3/library/itertools.html>`__ module in the standard library.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
