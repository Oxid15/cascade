"""
Copyright 2022-2024 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from coolname import generate

from . import Meta

default_keys = ["data", "dataset"]


class Version:
    def __init__(self, version: str):
        components = version.split(".")
        if len(components) != 2:
            raise ValueError(
                f"The string '{version}' is incorrect "
                f"version string with {len(components)} parts instead of 2"
            )
        major, minor = components
        self.major = int(major)
        self.minor = int(minor)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    @staticmethod
    def _check_other(other):
        if not isinstance(other, Version):
            raise TypeError(f"Can only compare Version with Version or string, got {type(other)}")

    def __eq__(self, other: Union["Version", str]) -> bool:
        if isinstance(other, str):
            other = Version(other)
        self._check_other(other)

        return self.major == other.major and self.minor == other.minor

    def __lt__(self, other: Union["Version", str]):
        if isinstance(other, str):
            other = Version(other)
        self._check_other(other)

        if self.major < other.major:
            return True
        elif self.major == other.major:
            return self.minor < other.minor
        return False

    def __gt__(self, other: Union["Version", str]):
        if isinstance(other, str):
            other = Version(other)
        self._check_other(other)

        if self.major > other.major:
            return True
        elif self.major == other.major:
            return self.minor > other.minor
        return False

    def __le__(self, other: Union["Version", str]) -> bool:
        return self < other or self == other

    def __ge__(self, other: Union["Version", str]) -> bool:
        return self > other or self == other

    def __repr__(self):
        return f"Version({self.major}.{self.minor})"

    def bump_major(self):
        return Version(f"{self.major + 1}.0")

    def bump_minor(self):
        return Version(f"{self.major}.{self.minor + 1}")


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug


def get_latest_commit_hash() -> Optional[str]:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return None


def get_uncommitted_changes() -> Optional[List[str]]:
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        result = result.stdout.strip()
        if result != "":
            return result.split("\n ")
        return None
    except Exception:
        return None


def get_python_version() -> str:
    info = sys.version
    return info


def parse_version(ver: str) -> Tuple[int, int, int]:
    numbers = re.findall("[0-9]+.[0-9]+.[0-9]+", ver)
    if len(numbers) == 1:
        major, minor, debug = numbers[0].split(".")
        return int(major), int(minor), int(debug)
    else:
        raise RuntimeError(f"Got unexpected version string {ver}")


def update_version(path: str, version: str) -> None:
    def write_version(path: str, version: str) -> None:
        meta[0]["cascade_version"] = version
        MetaHandler.write_dir(path, meta)

    from cascade.base import MetaHandler

    meta = MetaHandler.read_dir(path)

    ver = meta[0].get("cascade_version")
    if not ver:
        write_version(path, version)
        return

    old_parts = parse_version(ver)
    new_parts = parse_version(ver)

    for new, old in zip(new_parts, old_parts):
        if new > old:
            write_version(path, version)
            return


def skeleton(meta: Meta, keys: Optional[List[Any]] = None) -> List[List[Dict[Any, Any]]]:
    """
    Parameters
    ----------
    meta: Meta
        Meta of the pipeline
    keys: List[Any], optional
        The set of keys in meta where to search for previous dataset's meta.
        For example Concatenator when get_meta() is called stores meta of its
        datasets in the field called 'data'.
        If nothing given uses the default set of keys. Use this parameter only if
        your custom modifiers have additional fields you need to cover in this.

    Returns
    -------
    skeleton: List[List[Dict[Any, Any]]]
    """

    if keys is not None:
        keys += default_keys
    else:
        keys = default_keys

    skel = []
    # The pipeline is given - represent each one with a new list
    if isinstance(meta, list):
        for ds in meta:
            s = skeleton(ds)
            skel.append(s)
    # The dataset is given - add it to the list and search for any
    # additional info in it
    elif isinstance(meta, dict):
        if "name" in meta:
            s = {"name": meta["name"]}
        else:
            raise KeyError("Name not in meta")

        for key in keys:
            if key in meta:
                prev = skeleton(meta["data"])
                s[key] = prev
        skel.append(s)
    return skel


def migrate_repo_v0_13(path: str) -> None:
    """
    Changes format of meta data files written in previous
    versions to be compatible with 0.13.X

    Changes:
    - Metric formatting for compatibility with viewers of new version
    - If metrics are not scalar, saves them in ``old_metrics`` dict in meta
    - Sets the cascade_version key to the current version in repos, lines and models
    - Skips meta files if fails to read them

    Parameters
    ----------
    path : str
        Path to the container to migrate
    """
    from cascade.base import MetaHandler, MetaIOError
    from cascade.lines import ModelLine
    from cascade.metrics import Metric
    from cascade.repos import Repo, SingleLineRepo
    from tqdm import tqdm

    def process_metrics(metrics: Dict[str, Any]) -> Tuple[List[Metric], Dict[str, Any]]:
        if not isinstance(metrics, dict):
            return [], metrics

        new_style = []
        incompatible = {}
        for name in metrics:
            value = metrics[name]

            if hasattr(value, "__float__"):
                metric = Metric(name=name, value=value)
                new_style.append(metric)
            else:
                incompatible[name] = value
        return new_style, incompatible

    new_version = "0.13.0"

    root_meta = MetaHandler.read_dir(path)
    if root_meta[0]["type"] == "repo":
        repo = Repo(path)
    elif root_meta[0]["type"] == "line":
        line = ModelLine(path)
        repo = SingleLineRepo(line)
    else:
        print(f"Type {root_meta[0]['type']} is not supported")
        return

    for line in tqdm(repo.get_line_names(), desc=f"Migrating to {new_version}"):
        line_obj = ModelLine(os.path.join(repo.get_root(), line))
        for model in line_obj.get_model_names():
            try:
                meta = MetaHandler.read_dir(os.path.join(path, line, model))
            except MetaIOError as e:
                print(f"Failed to read meta: {e}")
                continue

            ver = meta[0].get("cascade_version")
            if ver:
                continue

            if "metrics" in meta[0]:
                new_style, incompatible = process_metrics(meta[0]["metrics"])
                meta[0]["metrics"] = new_style
                if incompatible:
                    meta[0]["old_metrics"] = incompatible

            meta[0]["cascade_version"] = new_version

            try:
                MetaHandler.write_dir(os.path.join(path, line, model), meta)
            except MetaIOError as e:
                print(f"Failed to write meta: {e}")
                continue

        try:
            update_version(os.path.join(path, line), new_version)
        except MetaIOError as e:
            print(f"Failed to update line version: {e}")

    try:
        update_version(path, new_version)
    except MetaIOError as e:
        print(f"Failed to update repo version: {e}")

    print("Done")
