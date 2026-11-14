from os import path
from setuptools import Extension, setup

if __name__ == "__main__":
    setup(
        ext_modules=[
            Extension(
                "unishox2",
                [
                    "unishox2_module.c",
                    path.join("Unishox2", "unishox2_fast.c"),
                ],
            )
        ]
    )
