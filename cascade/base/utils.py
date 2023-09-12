import os
from coolname import generate


def generate_slug() -> str:
    words = generate(3)
    slug = "_".join(words)
    return slug


def migrate_repo_v0_13(path: str) -> None:
    from cascade.models import ModelRepo, ModelLine, Metric, MetricType
    from cascade.base import MetaHandler
    from cascade.version import __version__

    def process_metrics(metrics):
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

    # Repo's meta file
    meta = MetaHandler.read_dir(path)[0]

    if "cascade_version" in meta:
        ver = meta["cascade_version"]

        major, minor, _ = ver.split('.')
        if int(major) >= 0 and int(minor) >= 13:
            return

    repo = ModelRepo(path)

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
