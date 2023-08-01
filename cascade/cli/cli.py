"""
Copyright 2022-2023 Ilia Moiseev

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
import glob
import click

from ..version import __version__
from ..base import MetaHandler, supported_meta_formats


@click.group
@click.pass_context
def cli(ctx):
    """
    Cascade CLI
    """
    ctx.ensure_object(dict)

    current_dir_full = os.getcwd()
    ctx.obj["cwd"] = current_dir_full
    current_dir = os.path.split(current_dir_full)[-1]
    click.echo(f"Cascade {__version__} in ./{current_dir}")
    meta_paths = glob.glob(os.path.join(current_dir_full, "meta.*"))
    meta_paths = [
        path
        for path in meta_paths
        if os.path.splitext(path)[-1] in supported_meta_formats
    ]

    if len(meta_paths) == 0:
        click.echo("It seems that there is no cascade objects here")
    elif len(meta_paths) == 1:
        meta = MetaHandler.read(meta_paths[0])
        ctx.obj["meta"] = meta
        ctx.obj["type"] = meta[0].get("type")
        ctx.obj["len"] = meta[0].get("len")
    else:
        click.echo(f"There are {len(meta_paths)} meta objects here")


@cli.command
@click.pass_context
def status(ctx):
    """
    Short description of what is present in the current folder
    """
    if ctx.obj.get("type"):
        output = f"This is {ctx.obj['type']}"
        if ctx.obj.get("len"):
            output += f" of len {ctx.obj['len']}"
        click.echo(output)
    

@cli.command
@click.pass_context
@click.option('-p', default=None)
def cat(ctx, p):
    """
    Full meta data of the object
    """
    from pprint import pformat

    if not p:
        if ctx.obj.get("meta"):
            click.echo(pformat(ctx.obj["meta"]))
    else:
        if ctx.obj.get("meta"):
            if ctx.obj["type"] == "line":
                from cascade.models import ModelLine
                container = ModelLine(ctx.obj["cwd"])
            elif ctx.obj["type"] == "repo":
                from cascade.models import ModelRepo
                container = ModelRepo(ctx.obj["cwd"])
            elif ctx.obj["type"] == "workspace":
                from cascade.models import Workspace
                container = Workspace(ctx.obj["cwd"])
            else:
                return

            try:
                p = int(p)
            except ValueError:
                pass

            meta = container.load_model_meta(p)
            click.echo(pformat(meta))


@cli.group
@click.pass_context
def view(ctx):
    """
    Different viewers
    """
    pass


@view.command
@click.pass_context
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8050)
@click.option("-l", type=int, help="The number of last lines to show")
@click.option("-m", type=int, help="The number of last models to show")
def history(ctx, host, port, l, m):
    if ctx.obj.get("meta"):
        type = ctx.obj["type"]
        if type == "workspace":
            from .models import Workspace
            container = Workspace(ctx.obj["cwd"])
        elif type == "repo":
            from .models import ModelRepo
            container = ModelRepo(ctx.obj["cwd"])
        elif type == "line":
            from .models import ModelLine
            container = ModelLine(ctx.obj["cwd"])
        else:
            click.echo(f"Cannot open History Viewer in object of type `{type}`")
            return

        from .meta import HistoryViewer
        HistoryViewer(container, last_lines=l, last_models=m).serve(host=host, port=port)


@view.command
@click.pass_context
@click.option("-p", type=int, default=50, help="Page size for table")
@click.option('-i', type=str, multiple=True, help="Metrics or params to include")
@click.option('-x', type=str, multiple=True, help="Metrics or params to exclude")
def metric(ctx, p, i, x):
    type = ctx.obj["type"]
    if type == "repo":
        from .models import ModelRepo
        container = ModelRepo(ctx.obj["cwd"])
    elif type == "line":
        from .models import ModelLine
        container = ModelLine(ctx.obj["cwd"])
    else:
        click.echo(f"Cannot open History Viewer in object of type `{type}`")
        return

    from .meta import MetricViewer
    i = None if len(i) == 0 else list(i)
    x = None if len(x) == 0 else list(x)
    MetricViewer(container).serve(page_size=p, include=i, exclude=x)


@view.command
@click.pass_context
def diff(ctx):
    from .meta import DiffViewer
    DiffViewer(ctx.obj["cwd"]).serve()


if __name__ == "__main__":
    cli(obj={})
