import fnmatch
import os
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_py import build_py as build_py_ori
from Cython.Build import cythonize


exclude = ["*.mod"]


class build_py(build_py_ori):
    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [
            (pkg, mod, file) for (pkg, mod, file) in modules
            if not any(
                fnmatch.fnmatchcase(pkg + '.' + mod, pat=pattern)
                for pattern in exclude
            )
        ]


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
    cmdclass={'build_py': build_py},
)

