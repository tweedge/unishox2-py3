#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "./unishox/unishox2.h"

static PyObject * py_unishox_compress(PyObject *self, PyObject *args) {
    char *uncompressed_input = NULL;
    /*
     * ":compress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of a string.
     */
    if (!PyArg_ParseTuple(args, "s:compress", &uncompressed_input)) {
        return NULL;
    }

    unsigned long input_length = strlen(uncompressed_input);
    char *output_buffer = (char *) malloc(input_length + 1);
    int compressed_size = unishox2_compress_simple(uncompressed_input, strlen(uncompressed_input), output_buffer);

    /*
     * Yay. Compression done. Let's build python bytes out of that raw memory!
     * No matter how big our buffer is, the "compressed_size" tells us where the actual
     * data stops. That's where we mark the end.
     */
    PyObject *py_multi_object = Py_BuildValue("y#k", output_buffer, compressed_size, input_length);
    free(output_buffer);
    return py_multi_object;
}

static PyObject * py_unishox_decompress(PyObject *self, PyObject *args) {
    char *compressed_data = NULL;
    Py_ssize_t compressed_data_size = 0;
    unsigned long original_data_size = 0;

    /*
     * ":decompress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of bytes.
     *
     * Note that we *have* to use "y#" because "y" does not allow for NULL bytes.
     */
    if (!PyArg_ParseTuple(args, "y#k:decompress", &compressed_data, &compressed_data_size, &original_data_size)) {
        return NULL;
    }

    /**
     * Notice that this is trusting user input for length, and there is no ability to try or catch.
     * You put in a number that's too small? Too bad. This *WILL* core dump.
     * 
     * It's a feature, sorta: https://github.com/siara-cc/Unishox/issues/5
     * 
     * I recommend calculating and storing the initial string length separately.
     */
    char *output_buffer = (char *) malloc(original_data_size + 1);
    int decompressed_size = unishox2_decompress_simple(compressed_data, compressed_data_size, output_buffer);

    PyObject *py_string_object = Py_BuildValue("s", output_buffer, decompressed_size);
    free(output_buffer);
    return py_string_object;
}

// Which methods are exposed to the python world, including their docstrings.
static PyMethodDef UnishoxMethods[] = {
    {"compress", py_unishox_compress, METH_VARARGS,
     "Compresses a string using unishox2 compression.\n\nArgs:\n    string: An input string\nReturns:\n    bytes: The input string compressed via unishox2 compression."},
    {"decompress", py_unishox_decompress, METH_VARARGS,
     "Decompresses a unishox2 compressed string.\n\nArgs:\n    bytes: A unishox2 compressed input string\n    int: The number of bytes to allocate for output\nReturns:\n    string: The input string decompressed via unishox2 decompression."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef unishox2_module = {
    PyModuleDef_HEAD_INIT,
    "unishox2",                                  // name of module
    "String compression library using Unishox2", // module documentation, may be NULL
    -1,                                          /* size of per-interpreter state of the
                                                    module, or -1 if the module keeps
                                                    state in global variables. */
    UnishoxMethods
};

PyMODINIT_FUNC
PyInit_unishox2(void) {
    return PyModule_Create(&unishox2_module);
}