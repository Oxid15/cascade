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
import os
import subprocess
from pprint import pformat
from typing import Any, Dict, List, Optional

import click


def cascade_config_imported(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "cascade.base.config" and node.names[0].name == "Config":
                return True
    return False


def find_config(tree: ast.Module) -> Optional[ast.ClassDef]:
    cfg_node = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if len(node.bases):
                for base in node.bases:
                    if base.id == "Config" and cascade_config_imported(tree):
                        cfg_node = node
    return cfg_node


def parse_value(value: ast.expr) -> Any:
    if isinstance(value, ast.Constant):
        return value.value
    elif isinstance(value, ast.Call):
        return str(value.func.id) + "()"
    return str(value)


def node2dict(cfg_node: ast.ClassDef) -> Dict[str, Any]:
    cfg_dict = {}
    for node in cfg_node.body:
        if isinstance(node, ast.Assign):
            key = node.targets[0].id
        elif isinstance(node, ast.AnnAssign):
            key = node.target.id
        else:
            continue

        cfg_dict[key] = parse_value(node.value)
    return cfg_dict


def modify_assignments(tree: ast.Module, cfg_node: ast.ClassDef, kwargs: Dict[str, Any]) -> str:
    for node in cfg_node.body:
        if isinstance(node, ast.Assign):
            target = node.targets[0].id
        elif isinstance(node, ast.AnnAssign):
            target = node.target.id
        else:
            continue
        if target in kwargs:
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
@click.option("-y", is_flag=True, expose_value=True, help="Confirm run")
@click.option("--log", type=str, default=None)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(script: str, y: bool, log: Optional[str], args: List[str]):
    click.echo(f"You are about to run {script}")

    with open(script, "r") as f:
        text = f.read()

    tree = ast.parse(text)
    cfg_node = find_config(tree)

    if cfg_node:
        cfg_dict = node2dict(cfg_node)
        kwargs = parse_args(args)
        cfg_dict.update(kwargs)

        click.echo("The config is:")
        click.echo(pformat(cfg_dict))
        click.echo("The arguments you passed:")
        click.echo(pformat(kwargs))

        text = modify_assignments(tree, cfg_node, kwargs)

    if not y:
        click.confirm("Confirm?", abort=True)

    if log:
        os.environ["CASCADE_RUN_LOG"] = os.path.abspath(log)

    script_globals = f'__file__ = "{script}"\n__name__ = "__main__"\n'
    text = script_globals + text

    process = subprocess.Popen(
        ["python", "-u", "-c", text],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=os.environ,
    )

    while True:
        line = process.stdout.readline().decode("utf-8").strip()
        if not line:
            break
        print(line)

        if log:
            with open(log, "a") as log_file:
                log_file.write(line + "\n")
