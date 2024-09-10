import fnmatch
import os
from pathlib import Path

from setuptools import setup, Extension
from Cython.Build import cythonize


def get_source_files():
    source_files = list(Path("mypkg").rglob("*.py"))
    source_files = [str(f) for f in source_files]
    return source_files

extensions = [
    Extension(
        name=os.path.splitext(f)[0].replace(os.path.sep, '.'),
        sources=[f],
        include_dirs=[os.path.dirname(f)]
    ) for f in get_source_files()
]

setup(
    ext_modules=cythonize(extensions),
)

