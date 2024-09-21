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

import ast
from typing import Any, Dict, Optional

import click


def cascade_config_imported(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "cascade.base.config" and node.names[0].name == "Config":
                return True
    return False


def find_config(tree: ast.Module):
    cfg_node = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if len(node.bases):
                for base in node.bases:
                    if base.id == "Config" and cascade_config_imported(tree):
                        cfg_node = node
    return cfg_node


def modify_assignments(tree: ast.Module, cfg_node: Optional[ast.ClassDef], kwargs: Dict[str, Any]) -> str:
    if cfg_node:
        for node in cfg_node.body:
            target = node.targets[0].id
            if isinstance(node, ast.Assign) and target in kwargs:
                node.value = ast.Constant(value=kwargs[target])
    return ast.unparse(tree)


def parse_args(args):
    kwargs = {}
    for keyval in args:
        key, val = keyval.split("=")
        key = key.strip()
        val = val.strip()

        kwargs[key] = val
    return kwargs


@click.command("run")
@click.argument("script", type=str)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(script, args):
    click.echo(f"You are about to run {script}")

    kwargs = parse_args(args)
    click.echo(kwargs)

    with open(script, "r") as f:
        text = f.read()

    tree = ast.parse(text)

    cfg_node = find_config(tree)

    text = modify_assignments(tree, cfg_node, kwargs)

    exec(text, globals())
