from typing import Any, Dict, List, Tuple
import os
import re
from coolname import generate


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug


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


def migrate_repo_v0_13(path: str) -> None:
    """
    Changes format of meta data files written in previous
    versions to be compatible with 0.13.X

    Changes:
    - Metric formatting for compatibility with viewers of new version
    - If metrics are not scalar, saves them in `old_metrics` dict in meta
    - Sets the cascade_version key to the current version in repos, lines and models
    - Skips meta files if fails to read them

    Parameters
    ----------
    path : str
        Path to the container to migrate
    """
    from tqdm import tqdm
    from cascade.base import MetaHandler, MetaIOError
    from cascade.models import ModelRepo, ModelLine, SingleLineRepo
    from cascade.metrics import Metric, MetricType

    def process_metrics(metrics: Dict[str, Any]) -> Tuple[List[Metric], Dict[str, Any]]:
        if not isinstance(metrics, dict):
            return [], metrics

        new_style = []
        incompatible = {}
        for name in metrics:
            value = metrics[name]

            if isinstance(value, MetricType):
                metric = Metric(
                    name=name,
                    value=value
                )
                new_style.append(metric)
            else:
                incompatible[name] = value
        return new_style, incompatible

    new_version = "0.13.0"

    root_meta = MetaHandler.read_dir(path)
    if root_meta[0]["type"] == "repo":
        repo = ModelRepo(path)
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
        print(f"Faile to update repo version: {e}")

    print("Done")
