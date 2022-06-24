#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "./Unishox2/unishox2.h"

static PyObject * py_unishox_compress(PyObject *self, PyObject *args) {
    char *uncompressed_input;
    Py_ssize_t uncompressed_input_size;
    /*
     * ":compress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of a string.
     */
    if (!PyArg_ParseTuple(args, "s#:compress", &uncompressed_input, &uncompressed_input_size)) {
        return NULL;
    }

    /*
     * We cannot say certainly that the compressed output will be smaller.
     * This current extra allocation is wasteful, and I'd like to get a better method.
     */
    int output_buffer_size = (uncompressed_input_size + 8) * 1.5;
    char *output_buffer = (char *) malloc(output_buffer_size);
    int compressed_size = unishox2_compress_simple(uncompressed_input, uncompressed_input_size, output_buffer);

    /*
     * Yay. Compression done. Let's build python bytes out of that raw memory!
     * No matter how big our buffer is, the "compressed_size" tells us where the actual
     * data stops. That's where we mark the end.
     */
    PyObject *py_multi_object = Py_BuildValue("y#i", output_buffer, compressed_size, uncompressed_input_size);
    free(output_buffer);
    return py_multi_object;
}

static PyObject * py_unishox_decompress(PyObject *self, PyObject *args) {
    char *compressed_data;
    Py_ssize_t compressed_data_size;
    int original_data_size;

    /*
     * ":decompress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of bytes.
     *
     * Note that we *have* to use "y#" because "y" does not allow for NULL bytes.
     */
    if (!PyArg_ParseTuple(args, "y#i:decompress", &compressed_data, &compressed_data_size, &original_data_size)) {
        return NULL;
    }

    /**
     * Notice that this is trusting user input for length, and there is no ability to try or catch.
     * You put in a number that's too small? Too bad. This *WILL* core dump. Too big? No problem.
     * 
     * It's a feature, sorta: https://github.com/siara-cc/Unishox/issues/5
     * 
     * I recommend calculating and storing the initial string length separately.
     */
    char *output_buffer = (char *) malloc(original_data_size + 1);
    int decompressed_size = unishox2_decompress_simple(compressed_data, compressed_data_size, output_buffer);

    PyObject *py_string_object = Py_BuildValue("s#", output_buffer, decompressed_size);
    free(output_buffer);
    return py_string_object;
}

// Which methods are exposed to the python world, including their docstrings.
static PyMethodDef UnishoxMethods[] = {
    {"compress", py_unishox_compress, METH_VARARGS,
     "Compresses a string using unishox2 compression.\n\nArgs:\n    string: An input string.\nReturns:\n    bytes: A unishox2-compressed array of bytes.\n    int: The number of bytes to allocate for output."},
    {"decompress", py_unishox_decompress, METH_VARARGS,
     "Decompresses a unishox2 compressed string.\n\nArgs:\n    bytes: A unishox2-compressed array of bytes.\n    int: The number of bytes to allocate for output.\nReturns:\n    string: The decompressed, near-original string."},
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