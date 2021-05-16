#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "./unishox/unishox2.h"

static PyObject *
py_unishox_compress(PyObject *self, PyObject *args)
{
    char *uncompressed_input;
    /*
     * ":compress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of a string.
     */
    if (!PyArg_ParseTuple(args, "s:compress", &uncompressed_input))
    {
        return NULL;
    }

    // 4KB is the default page size supported by many architectures. so lets allocating
    // an entire memory page.
    int output_buffer_size = 4096;

    // output_buffer will hold our (raw) compressed string data.
    char *output_buffer = (char *)malloc(output_buffer_size);
    int compressed_size = unishox2_compress_simple(uncompressed_input, strlen(uncompressed_input), output_buffer)
    /*
     * If the compressed string didn't fit into the first 4096, we will get 4097
     * eturned. So, we continue increasing memory until the compressed output fits.
     */
    while (output_buffer_size + 1 == compressed_size)
    {
        /*
         * increase memory usage.
         * I dont feel like this is ideal as it might heavily over-allocate on bigger
         * strings. But I do see that it is a good tradeoff between how many times we
         * have to run this loop and memory usage.
         */
        output_buffer_size *= 2;
        output_buffer = (char *)realloc(output_buffer, output_buffer_size);
        // try again. the while() on top then checks if it did fit this time around.
        compressed_size = unishox_compress(uncompressed_input, strlen(uncompressed_input), output_buffer, output_buffer_size);
    }
    /*
     * Yay. Compression done. Let's build python bytes out of that raw memory!
     * No matter how big our buffer is, the "compressed_size" tells us where the actual
     * data stops. That's where we mark the end.
     */
    PyObject *py_bytes_object = Py_BuildValue("y#", output_buffer, compressed_size);
    free(output_buffer);
    return py_bytes_object;
}

static PyObject *
py_unishox_decompress(PyObject *self, PyObject *args)
{
    char *compressed_data = NULL;
    Py_ssize_t compressed_data_size = 0;

    /*
     * ":decompress" leads to Python referencing this function correctly in the event of
     * an error during PyArg_ParseTuple, like when passing a list instead of bytes.
     *
     * Note that we *have* to use "y#" because "y" does not allow for NULL bytes.
     */
    if (!PyArg_ParseTuple(args, "y#:decompress", &compressed_data, &compressed_data_size))
    {
        return NULL;
    }

    // 4KB is the default page size supported by many architectures. so lets allocating
    // an entire memory page.
    int output_buffer_size = 4096;
    // output_buffer will hold our uncompressed string data.
    char *output_buffer = (char *)malloc(output_buffer_size);
    int decompressed_size = unishox2_compress_simple(compressed_data, compressed_data_size, output_buffer)
    /* If the compressed string didn't fit into the first 4096, we will get 4097
     * returned. So, we continue increasing memory until the compressed output fits.
     */
    while (output_buffer_size + 1 == decompressed_size)
    {
        /* increase memory usage.
         * I dont feel like this is ideal as it might heavily over-allocate on bigger
         * strings. But I do see that it is a good tradeoff between how many times we
         * have to run this loop and memory usage.
         */
        output_buffer_size *= 2;
        output_buffer = (char *)malloc(output_buffer_size);
        // try again. the while() on top then checks if it did fit this time around.
        decompressed_size = unishox_decompress(compressed_data, compressed_data_size, output_buffer, output_buffer_size);
    }
    /*
     * Yay. Decompression done. Let's build a python string out of that raw memory!
     * No matter how big our buffer is, the "decompressed_size" tells us where the
     * actual data stops. That's where we mark the end for our string.
     */
    output_buffer[decompressed_size] = 0;
    PyObject *py_string_object = Py_BuildValue("s", output_buffer);
    free(output_buffer);
    return py_string_object;
}

// Which methods are exposed to the python world, including their docstrings.
static PyMethodDef UnishoxMethods[] = {
    {"compress", py_unishox_compress, METH_VARARGS,
     "Compresses a string using Unishox compression.\n\nArgs:\n    string: An input string\nReturns:\n    bytes: The input string compressed via Unishox compression."},
    {"decompress", py_unishox_decompress, METH_VARARGS,
     "Decompresses a Unishox compressed string.\n\nArgs:\n    bytes: A Unishox compressed input string\nReturns:\n    string: The input string decompressed via Unishox decompression."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef Unishoxmodule = {
    PyModuleDef_HEAD_INIT,
    "Unishox",                                  // name of module
    "String compression library using Unishox", // module documentation, may be NULL
    -1,                                      /* size of per-interpreter state of the
                                                module, or -1 if the module keeps
                                                state in global variables. */
    UnishoxMethods};

PyMODINIT_FUNC
PyInit_Unishox(void)
{
    return PyModule_Create(&Unishoxmodule);
}