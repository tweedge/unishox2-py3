from codecs import open
from os import path

from setuptools import Extension, find_packages, setup

__version__ = "0.0.1"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="unishox2-py3",
    version=__version__,
    description="Small string compression using unishox2, supports Python 3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tweedge/unishox2-py3",
    license="BSD",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    keywords="unishox2 string compression",
    packages=find_packages(exclude=["docs", "tests*"]),
    ext_modules=[
        Extension(
            "unishox2",
            [
                path.join(here, "unishox2_module.c"),
                path.join(here, "unishox2", "unishox2.c"),
                path.join(here, "unishox", "unishox2.h")
            ],
        )
    ],
    include_package_data=True,
    author="Chris Partridge",
    author_email="tweedge-public@partridge.tech",
)
