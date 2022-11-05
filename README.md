# unishox2-py3

[![License](https://img.shields.io/github/license/tweedge/unishox2-py3)](https://github.com/tweedge/unishox2-py3)
[![Downloads](https://img.shields.io/pypi/dm/unishox2-py3)](https://pypi.org/project/unishox2-py3/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

This package enables Python projects to easily use Unishox2 from [siara-cc/Unishox2](https://github.com/siara-cc/Unishox2), which is a C library for compressing short strings. Unishox2 has many potential applications, and this package can enable developers to make use of it for several of those:

* ✅ Unicode-native text compression. Unishox2 is **NOT** English- or ASCII-only!
* ✅ Bandwidth and storage cost reduction for databases and/or cloud services.
* ⚠️ Byte columns can result in a faster retrieval speed when used as join keys in RDBMSes.
  * *Author's note: haven't tested this, but I'd trust the claim generally*
* ⛔️ Compression for low memory devices such as Arduino and ESP8266.
  * *Author's note: just use the C bindings for this, they're very approachable*

Want to learn more about Unishox2? Read the source paper [here](https://github.com/siara-cc/Unishox2/blob/master/Unishox_Article_2.pdf?raw=true).

### How to Use

This package is available [on PyPI](https://pypi.org/project/unishox2-py3/), and can be installed with `pip3 install unishox2-py3`. Please note that this package **only** supports Python3, and does not work for Python2 or below. You can see its CI status and testing matrix in this repository's [Actions tab](https://github.com/tweedge/unishox2-py3/actions).

Getting started with unishox2-py3 is easy. If you want to give it a try via the command line, you can use [demo.py](https://github.com/tweedge/unishox2-py3/blob/main/demo.py) to compress some sample strings or try one of your own.

If you're looking to integrate, unishox2-py3 currently provides two APIs that pass data to Unishox2's corresponding `simple` APIs - accepting the default optimization preset, which is good for most data. These are:

* `unishox2.compress(str)`
  * Arguments:
    * `str` - This requires a string as input (generally, Unicode-encoded).
  * Returns a tuple: 
    * `bytes` - The compressed data.
    * `int` - The original length of the string.
* `unishox2.decompress(bytes, int)`
  * Takes two arguments:
    * `bytes` - The compressed data.
    * `int` - The original length of the string.
  * Returns:
    * `str` - A string, the original data.

Taken together, this looks like:

```python
import unishox2

# the string we want to compress
original_data = "What the developers know:\n1. Whole codebase is spaghetti\n2. Also, spaghetti is delicious."

# drop that in as-is, nothing else is needed for compression
compressed_data, original_size = unishox2.compress(original_data)
# compressed_data now holds bytes, such as b'\x87\xbfi\x85\x1d\x9a\xe9\xfd ...'
# original_size now holds an integer, such as 89

# to get the original string back, we need compressed_data AND original_size
decompressed_data = unishox2.decompress(compressed_data, original_size)
# decompressed_data now holds a string, such as "What the developers know:\n..."
```

### Important Notes

First, you have to have the `original_size`, or know what the *maximum* `original_size` can be for your data, as Unishox2 does not dynamically allocate memory for the resultant string when decompressing. If you need to track the exact size (ex. if some documents are KB, where others are GB), and you are saving the Unishox2-compressed data to a database, you **must** store the `original_size` value as well.

As mentioned before, any reasonable maximum for the resultant data also works. So if you are storing usernames that must be 3-20 characters in length, you can skip saving the `original_size` and use 20 as the `original_size` for all values during decompression.

Conversely, if you give an `original_size` value that is too small, too little memory will be allocated. This means that Unishox2 will write past the memory boundary (as it's C under the hood, which is just bound to Python via a module), and your Python program will crash.

### OS/Architecture Support

Since unishox2-py3 includes a C library, it must be built specifically for each CPU architecture and OS in use. Wheels are built and tested for many platforms via [cibuildwheel](https://github.com/pypa/cibuildwheel), allowing for unishox2-py3 to be used with the following platforms out-of-the-box:

* Linux: x86_64, i686, aarch64, ppc64le, s390x
* MacOS: x86_64, arm64, universal2
* Windows: AMD64, x86

If you need another OS/architecture supported, please file [an issue](https://github.com/tweedge/unishox2-py3/issues/new) and I'm glad to look into supporting it.

### Performance

While Unishox doesn't provide *guaranteed* compression for *all* short strings (see the test cases for some examples where the output is larger than the input), it tends to provide better compression than many competitors in real-world usecases for short string compression. In addition, as unishox2-py3 is using a C module instead of reimplementing Unishox2 in Python, there is acceptable performance loss across most applications.

When tested on Reddit data (technical subreddits, mostly English-oriented, 3.3m entries), the average number of bytes required for storing each post's title was:
* Original: 60.34
* zlib(1): 61.83 (+2.47%)
* zlib(9): 61.80 (+2.42%)
* smaz: 43.46 (-27.98%)
* Unishox2: 40.08 (-33.58%)

And the average number of bytes required for storing each text post's body was:
* Original: 561.07
* zlib(1): 319.93 (-42.98%)
* zlib(9): 312.87 (-44.23%)
* smaz: 369.04 (-34.23%)
* Unishox2: 310.56 (-44.65%)

And the average number of bytes required for storing the URL that any link posts pointed to:
* Original: 25.72
* zlib(1): 30.08 (+16.96%)
* zlib(9): 30.08 (+16.96%)
* smaz: 20.78 (-19.21%)
* Unishox2: 19.76 (-23.16%)

Unishox2 shows clear benefits over traditional compressors when compressing short strings, and maintains comparable performance even to moderate-length documents. Unishox2 would be expected to pull farther ahead of smaz for non-English posts as well, though I don't have data to test that. I welcome a PR with additional performance tests.

### Integration Tests

The original test suite from [test_unishox2.c](https://github.com/siara-cc/Unishox/blob/d8fafe350446e4be3a05e06a0404a2223d4d972d/test_unishox2.c) has been copied.

Tests were added to ensure the Python-to-C binding is type safe:
- Ensuring `compress()` only takes strings
- Ensuring `decompress()` only takes bytes and an integer
  - Though it will still take a negative integer, and instantly crash, so... don't do that
- Ensuring `compress()` won't take a Unicode surrogate e.g. `\ud800`

Tests were also added to check certain edge cases:
- Ensuring Unishox2 allocates enough memory for rare, very-high-entropy strings which are enlarged when encoded by Unishox2
- Ensuring Unishox2 works with ASCII inputs

And finally, [hypothesis](https://hypothesis.readthedocs.io/en/latest/) based property testing was added to generate random inputs which:
- Build confidence that as long as a *minimum* length is known for strings, decompression will always work, and original_size doesn't need to be saved
  - This runs 25,000 tests which allocate 44 bytes <= x <= 1 gigabyte for decompression
- Build confidence that Unishox2 is resilient and functional when presented with arbitrary Unicode input
  - This runs 25,000 tests which generate valid Unicode of any length and composition

*Note: 25k property tests per test type are only used for testing when compiled to x86, tests of each built package (ex. for aarch64) only run 100 property tests per test type per package. This alongside other tests provides assurance that unishox2-py3 is working as intended, but not **as much** assurance as x86.*

### Credits

First and foremost, thank you to [Arun](https://github.com/siara-cc) of [Siara Logics](https://siara.cc/) for the incredible compression library - Unishox2 is lean, fast, and versatile. I am looking forward to using this in my projects and hope it benefits others as well.

In addition, this package is largely based on work from [originell/smaz-py3](https://github.com/originell/smaz-py3), and would not have been as quickly-developed or strongly-tested without Luis' lead.

Finally, I would like to thank [Josh Bicking](https://jibby.org) for his debugging insights and pragmatic thoughts on C as a whole.