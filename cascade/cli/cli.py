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

import click

from ..base import MetaHandler, MetaIOError
from .artifact import artifact
from .comment import comment
from .common import create_container
from .desc import desc
from .tag import tag
from .view import view


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
        ctx.obj["meta_fmt"] = MetaHandler.determine_meta_fmt(current_dir_full, "meta.*")
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
            container = create_container(ctx.obj["type"], ctx.obj["cwd"])
            if not container:
                return

            try:
                p = int(p)
            except ValueError:
                pass

            meta = container.load_model_meta(p)
            click.echo(pformat(meta))


@cli.command("migrate")
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


cli.add_command(artifact)
cli.add_command(comment)
cli.add_command(desc)
cli.add_command(tag)
cli.add_command(view)


if __name__ == "__main__":
    cli(obj={})
