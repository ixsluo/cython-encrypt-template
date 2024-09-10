# Cython-encrypt python project template

Package python project into wheel with specified .py files encrypted with cython, and excluded the encrypted .py files from wheel.

`Makefile`

Package logic:
1. determine the target wheel name (by `package_tag.py`)
2. find the excluded .py files and compile with cython (by `setup.py`)
3. build source distribution (in `$(TMP_DIST_DIR)/*.tar.gz`)
4. unpack the source distribution
5. build wheel distribution in the unpacked directory (in `$(TMP_DIST_DIR)/*/build/*.whl`)
6. copy to `build/<TARGETNAME>.whl`

`MANIFEST.in`

Files included and excluded from source distribution. **The excluded files are determined from here.**

`package_tag.py`

Prepare distribution name, version, build tag, python tag, abi tag, platform tag etc. Version is parsed by setuptools_scm. Python tag, abi tag and platform tag are parsed from system.

Refer to `python package_tag.py` for more usage.

`filter_files.py`

Filter the included or excluded package files.

Refer to `python filter_files.py` for more usage.

# Other notes

offline build: refer to `python -m build --no-isolation ...`