#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <limits.h>
#include <stdlib.h>
#include "./Unishox2/unishox2.h"

/*
 * Both Unishox2 entry points below are used in their length-checked form
 * (UNISHOX_API_WITH_OUTPUT_LEN, enabled in setup.py). The C decoder/encoder
 * signal "output did not fit" by returning exactly (capacity + 1); a
 * successful call always returns a length <= capacity. That lets us grow the
 * buffer and retry instead of trusting a caller-supplied size, so a wrong
 * length hint can no longer write past the allocation.
 */

/* Return codes for the internal grow-and-retry helpers (never valid lengths). */
#define USX_ERR_NOMEM (-1)
#define USX_ERR_RANGE (-2)

/*
 * Decompress `in` into a freshly allocated buffer of the exact final size.
 *
 * `hint` is the caller's optional length hint. When hint >= 0 the first
 * attempt uses exactly that capacity (fast path for callers that store the
 * length). When hint < 0 a capacity is estimated from the compressed size.
 * In both cases a too-small buffer is detected and retried with a larger one,
 * so the hint is advisory, never trusted. On success *out is set to a
 * malloc'd, NUL-terminated buffer and the decompressed length is returned.
 */
static int usx_decompress_alloc(const char *in, int in_len, long hint, char **out) {
  long cap;
  if (hint >= 0) {
    cap = hint;
  } else {
    cap = (long)in_len * 4 + 64;
    if (cap < 64)
      cap = 64;
    if (cap > INT_MAX - 1)
      cap = INT_MAX - 1;
  }

  for (;;) {
    char *buf = (char *)malloc((size_t)cap + 1);
    if (buf == NULL)
      return USX_ERR_NOMEM;

    int got = unishox2_decompress(in, in_len, buf, (int)cap, USX_PSET_DFLT);
    if (got >= 0 && got <= cap) {
      buf[got] = '\0';
      *out = buf;
      return got;
    }

    free(buf);
    if (cap >= INT_MAX - 1)
      return USX_ERR_RANGE;

    long next;
    if (cap == 0)
      next = 1;
    else if (cap > (INT_MAX - 1) / 2)
      next = INT_MAX - 1;
    else
      next = cap * 2;
    cap = next;
  }
}

/*
 * Compress `in` into a freshly allocated buffer of the exact final size,
 * growing on overflow. Bounded compression produces the same bytes as the
 * unbounded simple API, so this is byte-compatible with previous releases.
 */
static int usx_compress_alloc(const char *in, int in_len, char **out) {
  long cap = (long)in_len + 16;
  if (cap < 16)
    cap = 16;
  if (cap > INT_MAX - 1)
    cap = INT_MAX - 1;

  for (;;) {
    char *buf = (char *)malloc((size_t)cap + 1);
    if (buf == NULL)
      return USX_ERR_NOMEM;

    int got = unishox2_compress(in, in_len, buf, (int)cap, USX_PSET_DFLT);
    if (got >= 0 && got <= cap) {
      *out = buf;
      return got;
    }

    free(buf);
    if (cap >= INT_MAX - 1)
      return USX_ERR_RANGE;

    long next;
    if (cap == 0)
      next = 1;
    else if (cap > (INT_MAX - 1) / 2)
      next = INT_MAX - 1;
    else
      next = cap * 2;
    cap = next;
  }
}

static PyObject *py_unishox_compress(PyObject *self, PyObject *args, PyObject *kwargs) {
  static char *kwlist[] = {"string", "with_size", NULL};
  char *uncompressed_input;
  Py_ssize_t uncompressed_input_size;
  int with_size = 0; /* default: return bytes only */
  /*
   * ":compress" leads to Python referencing this function correctly in the event of
   * an error during PyArg_ParseTuple, like when passing a list instead of a string.
   *
   * with_size defaults to false, so compress() returns just the compressed
   * bytes. Pass with_size=True to also get the original length back as
   * (bytes, original_size) for callers that store or reuse it.
   */
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|p:compress", kwlist,
                                   &uncompressed_input, &uncompressed_input_size, &with_size)) {
    return NULL;
  }

  if (uncompressed_input_size > INT_MAX) {
    PyErr_SetString(PyExc_OverflowError,
                    "input is too large for Unishox2 (exceeds INT_MAX bytes)");
    return NULL;
  }

  char *output_buffer = NULL;
  int compressed_size = usx_compress_alloc(uncompressed_input, (int)uncompressed_input_size,
                                           &output_buffer);
  if (compressed_size == USX_ERR_NOMEM) {
    PyErr_NoMemory();
    return NULL;
  }
  if (compressed_size < 0) {
    PyErr_SetString(PyExc_MemoryError, "compressed output is too large for Unishox2");
    return NULL;
  }

  /*
   * We now know the exact compressed size. By default return only the bytes;
   * with_size=True additionally returns the original uncompressed size, which
   * decompress accepts as an optional hint.
   */
  PyObject *py_result;
  if (with_size) {
    py_result = Py_BuildValue("y#n", output_buffer, (Py_ssize_t)compressed_size,
                              (Py_ssize_t)uncompressed_input_size);
  } else {
    py_result = Py_BuildValue("y#", output_buffer, (Py_ssize_t)compressed_size);
  }
  free(output_buffer);
  return py_result;
}

static PyObject *py_unishox_decompress(PyObject *self, PyObject *args) {
  char *compressed_data;
  Py_ssize_t compressed_data_size;
  PyObject *length_obj = Py_None;

  /*
   * ":decompress" leads to Python referencing this function correctly in the event of
   * an error during PyArg_ParseTuple, like when passing a list instead of bytes.
   *
   * Note that we *have* to use "y#" because "y" does not allow for NULL bytes.
   *
   * The original length is optional: omitting it (or passing None) decompresses
   * without a stored length. When given it is only a hint; a value that is too
   * small is detected and retried with a larger buffer instead of crashing.
   */
  if (!PyArg_ParseTuple(args, "y#|O:decompress", &compressed_data, &compressed_data_size,
                        &length_obj)) {
    return NULL;
  }

  if (compressed_data_size > INT_MAX) {
    PyErr_SetString(PyExc_OverflowError,
                    "compressed input is too large for Unishox2 (exceeds INT_MAX bytes)");
    return NULL;
  }

  long length_hint = -1;
  if (length_obj != Py_None) {
    if (!PyLong_Check(length_obj)) {
      PyErr_SetString(PyExc_TypeError,
                      "original length must be an integer or None");
      return NULL;
    }
    length_hint = PyLong_AsLong(length_obj);
    if (length_hint == -1 && PyErr_Occurred())
      return NULL;
    if (length_hint < 0) {
      PyErr_SetString(PyExc_ValueError, "original length must not be negative");
      return NULL;
    }
    if (length_hint > INT_MAX) {
      PyErr_SetString(PyExc_OverflowError,
                      "original length is too large for Unishox2 (exceeds INT_MAX bytes)");
      return NULL;
    }
  }

  char *output_buffer = NULL;
  int decompressed_size = usx_decompress_alloc(compressed_data, (int)compressed_data_size,
                                               length_hint, &output_buffer);
  if (decompressed_size == USX_ERR_NOMEM) {
    PyErr_NoMemory();
    return NULL;
  }
  if (decompressed_size < 0) {
    PyErr_SetString(PyExc_MemoryError, "decompressed output is too large for Unishox2");
    return NULL;
  }

  PyObject *py_string_object =
      Py_BuildValue("s#", output_buffer, (Py_ssize_t)decompressed_size);
  free(output_buffer);
  return py_string_object;
}

// Which methods are exposed to the python world, including their docstrings.
static PyMethodDef UnishoxMethods[] = {
    {"compress", (PyCFunction)(void (*)(void))py_unishox_compress,
     METH_VARARGS | METH_KEYWORDS,
     "Compresses a string using unishox2 compression.\n\nArgs:\n    string: An input string.\n    with_size: If False (default), return just the compressed bytes. If True, return (bytes, original_length) so the length can be passed back to decompress as an optional hint.\nReturns:\n    bytes, or (bytes, int) when with_size is True."},
    {"decompress", py_unishox_decompress, METH_VARARGS,
     "Decompresses a unishox2 compressed string.\n\nArgs:\n    bytes: A unishox2-compressed array of bytes.\n    int: Optional original length hint. If omitted or None, the output buffer is sized automatically. A hint that is too small is handled safely (it is grown as needed).\nReturns:\n    string: The decompressed, near-original string."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef unishox2_module = {
    PyModuleDef_HEAD_INIT,
    "unishox2",
    "String compression library using Unishox2",
    0,
    UnishoxMethods
};

PyMODINIT_FUNC
PyInit_unishox2(void) {
    return PyModule_Create(&unishox2_module);
}
