from os import path
from setuptools import Extension, setup
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))


if __name__ == "__main__":
    setup(
        ext_modules=[
            Extension(
                "unishox2",
                [
                    path.join(here, "unishox2_module.c"),
                    path.join(here, "Unishox2", "unishox2.c"),
                ],
            )
        ]
    )
