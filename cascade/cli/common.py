from typing import Any


def create_container(type: str, cwd: str) -> Any:
    if type == "line":
        from cascade.models import ModelLine

        return ModelLine(cwd)
    elif type == "repo":
        from cascade.models import ModelRepo

        return ModelRepo(cwd)
    elif type == "workspace":
        from cascade.models import Workspace

        return Workspace(cwd)
    else:
        return
