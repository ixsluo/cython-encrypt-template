import os
from pathlib import Path

from Cython.Build import cythonize  # type: ignore
from setuptools import Extension, setup  # type: ignore

from filter_files import (
    find_all_package_files,
    find_all_packages,
    get_excluded_files,
    get_manifest_patterns,
)


def get_compile_files():
    _, exclude = get_manifest_patterns()
    files = find_all_package_files(find_all_packages())
    files = get_excluded_files(files, exclude)
    files = [f for f in files if f.endswith(".py")]
    return files


extensions = [
    Extension(
        name=os.path.splitext(f)[0].replace(os.path.sep, "."),
        sources=[f],
        include_dirs=[os.path.dirname(f)],
    )
    for f in get_compile_files()
]

setup(
    ext_modules=cythonize(extensions),
)
