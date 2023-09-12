from typing import Any, Dict, List, Tuple
import os
from coolname import generate


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug


def parse_version(meta: List[Dict[Any, Any]]):
    import re

    ver = meta[0]["cascade_version"]
    numbers = re.findall("[0-9]+.[0-9]+.[0-9]+", ver)
    if len(numbers) == 1:
        major, minor, debug = numbers[0].split(".")
        return int(major), int(minor), int(debug)
    else:
        raise RuntimeError(f"Got unexpected version string {ver}")


def migrate_repo_v0_13(path: str) -> None:
    from cascade.base import MetaHandler
    # Repo's meta file
    meta = MetaHandler.read_dir(path)[0]

    if "cascade_version" in meta:
        major, minor, _ = parse_version(meta)
        if int(major) >= 0 and int(minor) >= 13:
            print(f"Version is {major}.{minor}.{_} in {path}, no need to migrate")
            return

    # Import everythin AFTER migration is needed
    from cascade.models import ModelRepo, ModelLine, Metric, MetricType, SingleLineRepo
    from cascade.version import __version__

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

    if meta["type"] == "repo":
        repo = ModelRepo(path)
    elif meta["type"] == "line":
        line = ModelLine(path)
        repo = SingleLineRepo(line)
    else:
        print(f"Type {meta['type']} is not supported")
        return

    for line in repo.get_line_names():
        line_obj = ModelLine(line)
        for model in line_obj.model_names:
            meta = MetaHandler.read_dir(os.path.join(path, line, model))

            if "metrics" in meta[0]:
                new_style, incompatible = process_metrics(meta[0]["metrics"])
                meta[0]["metrics"] = new_style
                if incompatible:
                    meta[0]["old_metrics"] = incompatible

            meta[0]["cascade_version"] = __version__

            MetaHandler.write_dir(os.path.join(path, line, model), meta)
    print("Done")
