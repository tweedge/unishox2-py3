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
                # Use the length-checked API so the module can detect and recover
                # from undersized output buffers instead of writing past them.
                define_macros=[("UNISHOX_API_WITH_OUTPUT_LEN", "1")],
            )
        ]
    )
