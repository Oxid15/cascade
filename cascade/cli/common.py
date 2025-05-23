"""
Copyright 2022-2025 Ilia Moiseev

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

from typing import Any

import click

from ..base import MetaHandler, MetaIOError


def init_ctx(ctx, path):
    try:
        meta = MetaHandler.read_dir(path)
        ctx.obj["meta"] = meta
        ctx.obj["type"] = meta[0].get("type")
        ctx.obj["len"] = meta[0].get("len")
        ctx.obj["meta_fmt"] = MetaHandler.determine_meta_fmt(path, "meta.*")
    except MetaIOError as e:
        click.echo(e)


def create_container(type: str, cwd: str) -> Any:
    # "line" fallback here is for compatibility
    # with older versions
    if type in ("line", "model_line"):
        from cascade.lines import ModelLine

        return ModelLine(cwd)
    elif type == "data_line":
        from cascade.lines import DataLine

        return DataLine(cwd)
    elif type == "repo":
        from cascade.repos import Repo

        return Repo(cwd)
    elif type == "workspace":
        from cascade.workspaces import Workspace

        return Workspace(cwd)
    else:
        return
