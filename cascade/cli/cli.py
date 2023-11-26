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

import click

from ..base import MetaHandler, MetaIOError


def infer_container(type: str, cwd: str):
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


@click.group
@click.pass_context
def cli(ctx):
    """
    Cascade CLI
    """
    ctx.ensure_object(dict)

    current_dir_full = os.getcwd()
    ctx.obj["cwd"] = current_dir_full

    try:
        meta = MetaHandler.read_dir(current_dir_full)
        ctx.obj["meta"] = meta
        ctx.obj["type"] = meta[0].get("type")
        ctx.obj["len"] = meta[0].get("len")
    except MetaIOError as e:
        click.echo(e)
        raise e


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
@click.option("-p", default=None)
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
            container = infer_container(ctx.obj["type"], ctx.obj["cwd"])
            if not container:
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


@view.command("history")
@click.pass_context
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8050)
@click.option("-l", type=int, help="The number of last lines to show")
@click.option("-m", type=int, help="The number of last models to show")
@click.option("-p", type=int, default=3, help="Update period in seconds")
def view_history(ctx, host, port, l, m, p):  # noqa: E741
    if ctx.obj.get("meta"):
        container = infer_container(ctx.obj["type"], ctx.obj["cwd"])
        if not container:
            click.echo(f"Cannot open History Viewer in object of type `{ctx.obj['type']}`")
            return

        from ..meta import HistoryViewer
        HistoryViewer(container, last_lines=l, last_models=m, update_period_sec=p).serve(host=host, port=port)


@view.command("metric")
@click.pass_context
@click.option("-p", type=int, default=50, help="Page size for table")
@click.option("-i", type=str, multiple=True, help="Metrics or params to include")
@click.option("-x", type=str, multiple=True, help="Metrics or params to exclude")
def view_metric(ctx, p, i, x):
    type = ctx.obj["type"]
    if type == "repo":
        from ..models import ModelRepo
        container = ModelRepo(ctx.obj["cwd"])
    elif type == "line":
        from ..models import ModelLine
        container = ModelLine(ctx.obj["cwd"])
    else:
        click.echo(f"Cannot open Metric Viewer in object of type `{type}`")
        return

    from ..meta import MetricViewer
    i = None if len(i) == 0 else list(i)
    x = None if len(x) == 0 else list(x)
    MetricViewer(container).serve(page_size=p, include=i, exclude=x)


@view.command("diff")
@click.pass_context
def view_diff(ctx):
    from ..meta import DiffViewer
    DiffViewer(ctx.obj["cwd"]).serve()


@cli.group
def comment():
    """
    Manage comments
    """


@comment.command("add")
@click.pass_context
@click.option("-c", prompt="Comment: ")
def comment_add(ctx, c):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import Traceable

    tr = Traceable()
    tr.from_meta(ctx.obj["meta"])
    tr.comment(c)
    MetaHandler.write_dir(ctx.obj["cwd"], tr.get_meta())


@comment.command("ls")
@click.pass_context
def comment_ls(ctx):
    import pendulum

    if not ctx.obj.get("meta"):
        return

    comments = ctx.obj["meta"][0].get("comments")
    if comments:
        for comment in comments:
            date = pendulum.parse(comment["timestamp"]).diff_for_humans(pendulum.now())
            click.echo(
                f"{comment['id']:<s} | {comment['user']:<s} | {comment['host']:<s} | {date:<s} | {comment['message']:<s}"
            )


@comment.command("rm")
@click.pass_context
@click.argument("id")
def comment_rm(ctx, id):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import Traceable

    tr = Traceable()
    tr.from_meta(ctx.obj["meta"])
    tr.remove_comment(id)
    MetaHandler.write_dir(ctx.obj["cwd"], tr.get_meta())


@cli.group
@click.pass_context
def tag(ctx):
    """
    Manage tags
    """
    pass


@tag.command("add")
@click.pass_context
@click.argument("t", nargs=-1)
def tag_add(ctx, t):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import Traceable

    tr = Traceable()
    tr.from_meta(ctx.obj["meta"])
    tr.tag(t)
    MetaHandler.write_dir(ctx.obj["cwd"], tr.get_meta())


@tag.command("ls")
@click.pass_context
def tag_ls(ctx):
    if not ctx.obj.get("meta"):
        return

    tags = ctx.obj["meta"][0].get("tags")
    click.echo(tags)


@tag.command("rm")
@click.pass_context
@click.argument("t", nargs=-1)
def tag_rm(ctx, t):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import Traceable

    tr = Traceable()
    tr.from_meta(ctx.obj["meta"])
    tr.remove_tag(t)
    MetaHandler.write_dir(ctx.obj["cwd"], tr.get_meta())


@cli.command('migrate')
@click.pass_context
def migrate(ctx):
    """
    Automatic migration of objects to newer cascade versions
    """
    supported_types = ["repo", "line"]
    if not ctx.obj.get("type") in supported_types:
        click.echo(f"Cannot migrate {ctx.obj['type']}, only {supported_types} are supported")
        return

    from cascade.base.utils import migrate_repo_v0_13

    migrate_repo_v0_13(ctx.obj.get("cwd"))


@cli.group("artifact")
@click.pass_context
def artifact(ctx):
    """
    Manage artifacts
    """


@artifact.command("rm")
@click.pass_context
def artifact_rm(ctx):
    if ctx.obj["type"] != "model":
        click.echo(f"Cannot remove an artifact from {ctx.obj['type']}")

    raise NotImplementedError()


@cli.group("desc")
@click.pass_context
def desc(ctx):
    """
    Manage descriptions
    """


@desc.command("add")
@click.pass_context
@click.option("-d", prompt="Description: ")
def desc_add(ctx, d):
    if not ctx.obj.get("meta"):
        return

    from cascade.base import Traceable

    tr = Traceable()
    tr.from_meta(ctx.obj["meta"])
    tr.describe(d)
    MetaHandler.write_dir(ctx.obj["cwd"], tr.get_meta())


if __name__ == "__main__":
    cli(obj={})
