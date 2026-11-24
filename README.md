# unishox2-py3

[![License](https://img.shields.io/github/license/tweedge/unishox2-py3)](https://github.com/tweedge/unishox2-py3)
[![Downloads](https://img.shields.io/pypi/dm/unishox2-py3)](https://pypi.org/project/unishox2-py3/)
[![Written By](https://img.shields.io/badge/written%20by-some%20nerd-red.svg)](https://chris.partridge.tech)
[![Follow author on Bluesky](https://img.shields.io/bluesky/followers/tweedge.net)](https://bsky.app/profile/tweedge.net)
[![Follow author on Mastodon](https://img.shields.io/mastodon/follow/108210086817505115?domain=https%3A%2F%2Fcybersecurity.theater)](https://cybersecurity.theater/@tweedge)

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

* `unishox2.compress(str, with_size=False)`
  * Arguments:
    * `str` - This requires a string as input (generally, Unicode-encoded).
    * `with_size` - *(optional, default `False`)* When `False`, returns just the compressed bytes. When `True`, returns a tuple of the compressed bytes and the original length, for callers that want to store the size.
  * Returns, when `with_size=False` (the default):
    * `bytes` - The compressed data.
  * Returns, when `with_size=True`, a tuple:
    * `bytes` - The compressed data.
    * `int` - The original length of the string.
* `unishox2.decompress(bytes, int=None)`
  * Takes two arguments, the second optional:
    * `bytes` - The compressed data.
    * `int` - *(optional)* The original length of the string. It is used only as a size hint. If omitted (or `None`), the output buffer is sized automatically. A hint that is too small is detected and the buffer is grown, so it can never write past the allocation.
  * Returns:
    * `str` - A string, the original data.

Taken together, this looks like:

```python
import unishox2

# the string we want to compress
original_data = "What the developers know:\n1. Whole codebase is spaghetti\n2. Also, spaghetti is delicious."

# compress returns just the bytes - no length to track
compressed_data = unishox2.compress(original_data)
# compressed_data now holds bytes, such as b'\x87\xbfi\x85\x1d\x9a\xe9\xfd ...'

# decompress needs nothing else
decompressed_data = unishox2.decompress(compressed_data)
# decompressed_data now holds a string, such as "What the developers know:\n..."

# if you also want the original length (e.g. to store it), ask for it
compressed_data, original_size = unishox2.compress(original_data, with_size=True)
# original_size now holds an integer, such as 89 - optional, use it as a hint
decompressed_data = unishox2.decompress(compressed_data, original_size)
```

### Important Notes

You do **not** need to store the `original_size` to decompress. `compress()` returns just the bytes by default and `decompress()` sizes the output buffer for you, so nothing else needs to be saved. If you pass a length hint and it is too small, it is handled safely (the buffer grows as needed) rather than crashing.

If you want the original length for your own reasons, call `compress(..., with_size=True)` to get it back and pass it to `decompress()` as an optional hint. That lets the output buffer be allocated exactly once instead of being grown, which is slightly faster. A maximum (for example 20 for usernames that must be 3-20 characters) is also a safe hint.

**Migrating from 1.x:** earlier versions returned `(bytes, original_size)` from `compress()`. In 2.0 `compress()` returns only `bytes`; pass `with_size=True` to get the old tuple back. `decompress()` still accepts an optional length, so code that stored the size keeps working.

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
- Ensuring `decompress()` only takes bytes and an optional integer
  - The integer is a size hint; a negative value raises `ValueError`
  - A hint that is too small is grown automatically instead of writing past the buffer
- Ensuring `compress()` won't take a Unicode surrogate e.g. `\ud800`

Tests were also added to check certain edge cases:
- Ensuring Unishox2 allocates enough memory for rare, very-high-entropy strings which are enlarged when encoded by Unishox2
- Ensuring Unishox2 works with ASCII inputs

And finally, [hypothesis](https://hypothesis.readthedocs.io/en/latest/) based property testing was added to generate random inputs which:
- Build confidence that decompression works for any non-negative length hint, from 0 up to 1 gigabyte (a too-small hint is recovered from, not trusted)
  - This runs 25,000 tests which pass 0 bytes <= x <= 1 gigabyte as the hint for decompression
- Build confidence that Unishox2 is resilient and functional when presented with arbitrary Unicode input
  - This runs 25,000 tests which generate valid Unicode of any length and composition

*Note: 25k property tests per test type are only used for testing when compiled to x86, tests of each built package (ex. for aarch64) only run 100 property tests per test type per package. This alongside other tests provides assurance that unishox2-py3 is working as intended, but not **as much** assurance as x86.*

### Credits

First and foremost, thank you to [Arun](https://github.com/siara-cc) of [Siara Logics](https://siara.cc/) for the incredible compression library - Unishox2 is lean, fast, and versatile. I am looking forward to using this in my projects and hope it benefits others as well.

In addition, this package is largely based on work from [originell/smaz-py3](https://github.com/originell/smaz-py3), and would not have been as quickly-developed or strongly-tested without Luis' lead.

Finally, I would like to thank [Josh Bicking](https://jibby.org) for his debugging insights and pragmatic thoughts on C as a whole.