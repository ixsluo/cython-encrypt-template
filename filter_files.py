import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path

from setuptools import find_packages  # type: ignore
from setuptools.config.pyprojecttoml import read_configuration  # type: ignore


def find_all_packages(pyproject="pyproject.toml"):
    config = read_configuration(pyproject)
    packages_config = config.get("tool", {}).get("setuptools", {}).get("packages", {})

    if isinstance(packages_config, list):
        # 如果packages是一个列表，直接使用
        packages = packages_config
    elif isinstance(packages_config, dict) and "find" in packages_config:
        # 如果packages是一个字典并且包含"find"键，使用find_packages()
        find_config = packages_config["find"]
        where = find_config.get("where", ["."])
        include = find_config.get("include", ["*"])
        exclude = find_config.get("exclude", [])
        packages = find_packages(
            where=where[0] if isinstance(where, list) else where,
            include=include,
            exclude=exclude,
        )
    else:
        # 如果没有配置，使用默认的find_packages()
        packages = find_packages()
    # print(packages)
    return packages


def find_all_package_files(packages):
    all_files = []
    for package in packages:
        package_dir = package.replace(".", os.path.sep)
        for root, _, files in os.walk(package_dir):
            for file in files:
                all_files.append(os.path.join(root, file))
    return list(set(all_files))


def get_manifest_patterns(fmanifest="MANIFEST.in"):
    include = []
    exclude = []
    with open(fmanifest, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                items = line.split()
                if items[0] == "include":
                    include.extend(f".//{pat}" + pat for pat in items[1:])
                elif items[0] == "exclude":
                    exclude.extend(f".//{pat}" for pat in items[1:])
                elif items[0] == "recursive-include":
                    d, *pats = items[1:]
                    include.extend(f"./{d}/**/{pat}" for pat in pats)
                elif items[0] == "recursive-exclude":
                    d, *pats = items[1:]
                    exclude.extend(f"./{d}/**/{pat}" for pat in pats)
                elif items[0] == "global-include":
                    include.extend(f".//**/{pat}" for pat in items[1:])
                elif items[0] == "global-exclude":
                    exclude.extend(f".//**/{pat}" for pat in items[1:])
                elif items[0] == "graft":
                    include.extend(f".//{pat}/**/*" for pat in items[1:])
                elif items[0] == "prune":
                    exclude.extend(f".//{pat}/**/*" for pat in items[1:])
                else:
                    print(f"Unknown line: {line}", file=sys.stderr)
    return (
        include,
        exclude,
    )


def match_path(path, pattern):
    path = Path(path)
    pattern_parts = Path(pattern).parts

    def match_recursive(path_parts, pattern_parts):
        if not pattern_parts:
            return not path_parts
        if not path_parts:
            return all(part == "**" for part in pattern_parts)

        if pattern_parts[0] == "**":
            if len(pattern_parts) == 1:
                return True
            for i in range(len(path_parts)):
                if match_recursive(path_parts[i:], pattern_parts[1:]):
                    return True
            return False
        else:
            matched = fnmatch.fnmatch(path_parts[0], pattern_parts[0])
            return matched and match_recursive(path_parts[1:], pattern_parts[1:])

    return match_recursive(path.parts, pattern_parts)


def get_excluded_files(files, exclude=None):
    if exclude is None:
        return []
    else:
        exclude = [re.sub(r"^\./{1,2}", "", pat) for pat in exclude]
        return [f for f in files if any(match_path(f, pat) for pat in exclude)]


def get_included_files(files, exclude=None):
    if exclude is None:
        return files
    else:
        exclude = [re.sub(r"^\./{1,2}", "", pat) for pat in exclude]
        return [f for f in files if all(not match_path(f, pat) for pat in exclude)]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find included or excluded files in packages filtered by MANIFEST.in",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("mode", help="filter mode, i[nclude] or e[xclude]")
    parser.add_argument("-p", dest="pyproject", default="pyproject.toml", help="To find packages from")  # fmt: skip
    parser.add_argument("-m", dest="manifest", default="MANIFEST.in", help="To find filters from")  # fmt: skip

    opts = parser.parse_args()
    return opts


def main():
    opts = parse_args()
    all_files = find_all_package_files(find_all_packages(opts.pyproject))
    include, exclude = get_manifest_patterns(opts.manifest)
    if opts.mode.startswith("i"):
        files = get_included_files(all_files, exclude)
    elif opts.mode.startswith("e"):
        files = get_excluded_files(all_files, exclude)
    else:
        raise ValueError(f"Unknown mode: {opts.mode}")
    for f in files:
        print(f)


if __name__ == "__main__":
    main()
