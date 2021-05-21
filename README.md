# unishox2-py3

[![License](https://img.shields.io/github/license/tweedge/unishox2-py3)](https://github.com/tweedge/unishox2-py3)
[![Downloads](https://img.shields.io/pypi/dm/unishox2-py3)](https://pypi.org/project/unishox2-py3/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

This package enables Python projects to easily use Unishox2 from [siara-cc/Unishox](https://github.com/siara-cc/Unishox/), which is a C library for compressing short strings. Unishox2 has many potential applications, and this package can enable developers to make use of it for several of those:

* ✅ Unicode-native text compression. Unishox2 is **NOT** English- or ASCII-only!
* ✅ Bandwidth and storage cost reduction for databases and/or cloud services.
* ⚠️ Byte columns can result in a faster retrieval speed when used as join keys in RDBMSes.
  * *Author's note: haven't tested this, but I'd trust the claim generally*
* ⛔️ Compression for low memory devices such as Arduino and ESP8266.
  * *Author's note: just use the C bindings for this, they're very approachable*

Want to learn more about Unishox2? Read the source paper [here](https://raw.githubusercontent.com/siara-cc/Unishox/master/Unishox_Article_2.pdf).

### How to Use

This package is available [on PyPI](https://pypi.org/project/unishox2-py3/), and can be installed with `pip3 install unishox2-py3`. Please note that this package **only** supports Python3, and does not work for Python2 or below. You can see its CI status and testing matrix in this repository's [Actions tab](https://github.com/tweedge/unishox2-py3/actions).

Getting started with unishox2-py3 is easy. If you want to give it a try via the command line, you can use [demo.py](https://github.com/tweedge/unishox2-py3/blob/main/demo.py) to compress some sample strings or try one of your own.

If you're looking to integrate, unishox2-py3 currently provides two APIs that pass data to Unishox2's corresponding `simple` APIs - accepting the default optimization preset, which is good for most data. These are:

* `unishox2.compress(str)`
  * Arguments:
    * `str` - This requires a Unicode string as input (generally, this is your default in Python).
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

The last note to make is that Unishox2 doesn't guarantee 1:1 parity with the source text. In particular, full-stops will be assigned during decompression in a 'best-guess' manner:

>6.11 Encoding punctuation
>• Some languages such as Japanese and Chinese use their own punctuation characters. For example, full-stop is indicated using U+3002 which is represented visually as a small circle.
>• So when encountering a Japanese full-stop, the special code for full-stop is used, only in this case, the decoder is expected to decode it as U+3002 instead of ’.’. In general, if the prior Unicode character is greater than U+3000, then the special full-stop is decoded.
> ...

Additional discussion on the above is [here](https://github.com/siara-cc/Unishox/issues/6).

### Performance

While Unishox doesn't provide *guaranteed* compression for *all* short strings (see the test cases for some examples where the output is larger than the input), it tends to provide better compression than many competitors in real-world usecases for short string compression. In addition, as unishox2-py3 is using a C module instead of reimplementing Unishox2 in Python, there is minimal performance loss across most applications.

When tested on Reddit data (technical subreddits, mostly English-oriented, ~3m entries), the average number of bytes required for storing each post's title was:
* Original: 125.12
* zlib(1): 94.82 (-24.21%)
* zlib(9): 94.80 (-24.23%)
* smaz: 76.45 (-38.90%)
* Unishox2: 73.07 (-41.60%)

And the average number of bytes required for storing each post's body text was:
* Original: 714.82
* zlib(1): 352.95 (-50.62%)
* zlib(9): 345.90 (-51.61%)
* smaz: 401.96 (-43.76%)
* Unishox2: 343.58 (-51.93%)

Unishox2 would be expected to pull farther ahead of smaz for non-English posts as well, though I don't have data to test that. I welcome a PR with additional tests.

### Credits

First and foremost, thank you to [Arun](https://github.com/siara-cc) of [Siara Logics](https://siara.cc/) for the incredible compression library - Unishox2 is lean, fast, and versatile. I am looking forward to using this in my projects and hope it benefits others as well.

In addition, this package is largely based on work from [originell/smaz-py3](https://github.com/originell/smaz-py3), and would not have been as quickly-developed or strongly-tested without Luis' lead.

Finally, I would like to thank [Josh Bicking](https://jibby.org) for his debugging insights and pragmatic thoughts on C as a whole.