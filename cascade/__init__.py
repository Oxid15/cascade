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


__version__ = "0.13.0-alpha"
__author__ = "Ilia Moiseev"
__author_email__ = "ilia.moiseev.5@yandex.ru"

import os
import glob
import click
from .base import MetaHandler, supported_meta_formats


@click.group()
@click.pass_context
def cli(ctx):
    """
    Cascade CLI
    """
    ctx.ensure_object(dict)

    current_dir_full = os.getcwd()
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
    else:
        click.echo(f"There are {len(meta_paths)} meta objects here")


@cli.command()
@click.pass_context
def status(ctx):
    """
    Short description of what is present in the current folder
    """
    if ctx.obj:
        output = f"This is {ctx.obj['meta'][0]['type']}"
        if ctx.obj["meta"][0].get("len"):
            output += f" of len {ctx.obj['meta'][0]['len']}"
        click.echo(output)


@cli.command()
@click.pass_context
def cat(ctx):
    """
    Full meta data of the current object
    """
    from pprint import pformat

    if ctx.obj:
        click.echo(pformat(ctx.obj["meta"]))


@cli.command()
@click.pass_context
def view(ctx):
    """
    Different viewers
    """
    pass


if __name__ == "__main__":
    cli(obj={})
