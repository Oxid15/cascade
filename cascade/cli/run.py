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
import re
import shutil
import subprocess
import warnings
from pprint import pformat
from typing import Any, Dict, List, Optional

import click
import pendulum
from cascade.base import MetaHandler


def cascade_config_imported(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "cascade.base.config" and node.names[0].name == "Config":
                return True
            if node.module == "cascade.base" and node.names[0].name == "Config":
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
    for key, val in zip(args[::2], args[1::]):
        key = re.sub(r"^-{1,2}\b", "", key)
        kwargs[key] = val
    return kwargs


def generate_run_id() -> str:
    now = pendulum.now().format("YYYYMMDD_HHmmss_SS")
    return now


class CascadeRun:
    def __init__(self, log: bool, config: Dict[str, Any], overrides: Dict[str, Any]) -> None:
        self.log = log
        self.config = config
        self.overrides = overrides

        base = os.getcwd()
        run_id = generate_run_id()
        self.run_dir = os.path.join(base, ".cascade", run_id)
        os.environ["CASCADE_RUN_DIR"] = self.run_dir

    def __enter__(self):
        os.makedirs(self.run_dir)

        MetaHandler.write(os.path.join(self.run_dir, "cascade_config.json"), self.config)
        MetaHandler.write(os.path.join(self.run_dir, "cascade_overrides.json"), self.overrides)

        return self

    def __exit__(self, *args):
        run_path = self.run_dir
        try:
            shutil.rmtree(run_path)
        except Exception as e:
            warnings.warn(
                f"Failed to remove run folder in {run_path} with the following error: {e}"
            )
        return False

    def run_script(self, script: str, text: str) -> None:
        script_globals = f'__file__ = "{script}"\n__name__ = "__main__"\n'
        text = script_globals + text

        process = subprocess.Popen(
            ["python", "-u", "-c", text],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=os.environ,
        )

        if self.log:
            logs_dir = os.path.join(self.run_dir, "logs")
            os.makedirs(logs_dir)

        while True:
            line = process.stdout.readline().decode("utf-8").strip()
            if not line:
                break
            print(line)

            if self.log:
                with open(os.path.join(logs_dir, "cascade_run.log"), "a") as log_file:
                    log_file.write(line + "\n")


@click.command("run", context_settings={"ignore_unknown_options": True})
@click.argument("script", type=str)
@click.option("-y", is_flag=True, expose_value=True, help="Confirm run")
@click.option("--log", is_flag=True, default=False)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(script: str, y: bool, log: Optional[str], args: List[str]):
    click.echo(f"You are about to run {script}")

    with open(script, "r") as f:
        text = f.read()

    tree = ast.parse(text)
    cfg_node = find_config(tree)

    if cfg_node:
        cfg_dict = node2dict(cfg_node)
        click.echo("The config is:")
        click.echo(pformat(cfg_dict))

        kwargs = parse_args(args)
        click.echo("The arguments you passed:")
        click.echo(pformat(kwargs))

        for key in kwargs:
            if key in cfg_dict:
                cfg_dict[key] = kwargs[key]
            else:
                raise KeyError(f"Key `{key}` is missing in the original config")

        text = modify_assignments(tree, cfg_node, kwargs)
    else:
        cfg_dict = {}
        kwargs = {}

    if not y:
        click.confirm("Confirm?", abort=True)

    with CascadeRun(log, cfg_dict, kwargs) as run:
        run.run_script(script, text)
