import argparse
import platform
import re
import subprocess
import sys
from pathlib import Path

from setuptools.config.pyprojecttoml import read_configuration  # type: ignore
from build._util import parse_wheel_filename
from packaging import tags


def get_distribution(distribution=None):
    if distribution is None:
        return read_configuration("pyproject.toml")["project"]["name"]
    else:
        return str(distribution)


def get_version(version=None):
    if version is None:
        import setuptools_scm  # type: ignore
        import setuptools_scm._get_version_impl  # type: ignore

        # v = setuptools_scm._get_version_impl.get_version(setuptools_scm.Configuration(root="."))
        v = setuptools_scm._get_version_impl.get_version()
    else:
        v = str(version)
    return v


def get_build_tag(build_tag=""):
    return build_tag


def get_python_tag():
    return f"py{sys.version_info.major}{sys.version_info.minor}"


def get_abi_tag():
    compatible_tags = list(tags.sys_tags())
    if compatible_tags:
        return compatible_tags[0].abi
    return "none"


def get_platform_tag():
    if sys.platform.startswith("linux"):
        platform_name = "linux"
    elif sys.platform == "darwin":
        platform_name = "darwin"
    elif sys.platform == "win32":
        platform_name = "win"
    else:
        platform_name = sys.platform
    arch = platform.machine().lower()
    if platform_name == "linux":
        try:
            glibc_version = subprocess.check_output(
                ["ldd", "--version"], stderr=subprocess.STDOUT
            ).decode()
            glibc_match = re.search(r"GLIBC (\d+\.\d+)", glibc_version)
            if glibc_match:
                glibc_version = f"_glibc{glibc_match.group(1)}"
        except:
            glibc_version = ""
    else:
        glibc_version = ""
    return f"{platform_name}_{arch}{glibc_version}".replace("-", "_")


def get_wheel_tags(wheel_name):
    m = parse_wheel_filename(wheel_name)
    try:
        tags = (
            m["distribution"],
            m["version"],
            m["build_tag"],
            m["python_tag"],
            m["abi_tag"],
            m["platform_tag"],
        )
    except Exception as e:
        raise ValueError(f"{wheel_name} is not a valid wheel name") from e
    else:
        # tags = [tag if tag is not None else '' for tag in tags]
        return tags


def modify_wheel_name(wheel_name):
    wheel_name = Path(wheel_name).name
    (
        distribution,
        version,
        build_tag,
        python_tag,
        abi_tag,
        platform_tag,
    ) = get_wheel_tags(wheel_name)
    abi_tag = get_abi_tag()
    platform_tag = get_platform_tag()
    tag = "-".join(
        t
        for t in [distribution, version, build_tag, python_tag, abi_tag, platform_tag]
        if t
    )
    return f"{tag}.whl"


def set_package_fname(args):
    distribution = get_distribution(args.distribution)
    version = get_version(args.version)
    build_tag = args.build_tag
    python_tag = get_python_tag()
    abi_tag = get_abi_tag()
    platform_tag = get_platform_tag()
    tag = "-".join(
        t
        for t in [distribution, version, build_tag, python_tag, abi_tag, platform_tag]
        if t
    )
    pkg_fname = f"{tag}"
    if parse_wheel_filename(pkg_fname + ".whl") is None:
        raise ValueError(f"Result {pkg_fname}.whl is not a valid wheel name")
    return pkg_fname


def parse_args(print_help=False):
    parser = argparse.ArgumentParser()
    parser.set_defaults(name="")
    subparsers = parser.add_subparsers(
        title="subcommands",
    )

    wheel = subparsers.add_parser("wheel", help="replace abi from given wheel name")
    wheel.set_defaults(name="wheel", func=modify_wheel_name)
    wheel.add_argument("wheel", nargs="+", help="wheel names, only the first one is used.")

    setname = subparsers.add_parser("set", help="set package filename without suffix")
    setname.set_defaults(name="setname", func=set_package_fname)
    setname.add_argument("-d", dest="distribution", help="set distribution name, default read from pyproject.toml.")  # fmt: skip
    setname.add_argument("-v", dest="version", help="set version, default use setuptools_scm.")  # fmt: skip
    setname.add_argument("-b", dest="build_tag", default="", help="set build tag, default not set.")  # fmt: skip

    if print_help:
        parser.print_help()

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.name == "wheel":
        custom_wheel_name = args.func(args.wheel[0])
        print(custom_wheel_name)
    elif args.name == "setname":
        custom_wheel_name = args.func(args)
        print(custom_wheel_name)
    else:
        parse_args(True)
