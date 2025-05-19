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

import ast
import os
import re
import shutil
import subprocess
import sys
import warnings
from pprint import pformat
from typing import Any, Dict, List, Optional

import click
import pendulum
from cascade.base import MetaHandler


class RunFailedException(RuntimeError): ...  # noqa: E701


def cascade_config_imported(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "cascade.base.config" and node.names[0].name == "Config":
                return True
            if node.module == "cascade.base" and node.names[0].name == "Config":
                return True
    return False


def find_config(tree: ast.Module) -> Optional[ast.ClassDef]:
    """
    Returns the first node that is cascade.base.Config.
    Returns before checking if Config import was not detected.
    Raises if more than one configs found - to actively restrict this
    until needed.
    """

    if not cascade_config_imported(tree):
        return None

    cfg_node = None
    more_than_one = False
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if len(node.bases):
                for base in node.bases:
                    if getattr(base, "id", None) == "Config":
                        if cfg_node is not None:
                            more_than_one = True
                        cfg_node = node
    if more_than_one:
        raise NotImplementedError(
            "Found more than one Config in a single file."
            " This Cascade version does not support multiple configs."
            " However, it may be implemented in the future."
            " Please, write me a GitHub issue if this functionality is needed"
        )

    return cfg_node


def parse_value(value: ast.expr) -> Any:
    """
    Create node representation for dict
    that will be printed
    """

    if sys.version_info < (3, 9):
        if isinstance(value, ast.NameConstant):
            return value.value
        elif isinstance(value, ast.Num):
            return value.n
        elif isinstance(value, ast.Str):
            return value.s

    if isinstance(value, ast.Constant):
        return value.value
    elif isinstance(value, ast.Call):
        return str(value.func.id) + "()"
    elif isinstance(value, ast.List):
        return [parse_value(v) for v in value.elts]
    elif isinstance(value, ast.Tuple):
        return tuple(parse_value(v) for v in value.elts)
    elif isinstance(value, ast.Set):
        return set(parse_value(v) for v in value.elts)
    elif isinstance(value, ast.Dict):
        return {parse_value(k): parse_value(v) for k, v in zip(value.keys, value.values)}
    else:
        raise ValueError(f"Unsupported config field type: {value} in {unparse_method(value)}")


# ast.unparse exists since python 3.9
# for older versions Cascade will require external package

if sys.version_info < (3, 9):
    import astunparse

    unparse_method = astunparse.unparse
else:
    unparse_method = ast.unparse


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
    """
    Overrides cascade.base.Config class definition with user-provided values
    """
    for node in cfg_node.body:
        if isinstance(node, ast.Assign):
            target = node.targets[0].id
        elif isinstance(node, ast.AnnAssign):
            target = node.target.id
        else:
            continue
        if target in kwargs:
            if sys.version_info < (3, 9):
                node.value = ast.NameConstant(kwargs[target], kind=None)
            else:
                node.value = ast.Constant(value=kwargs[target])
    return unparse_method(tree)


def parse_args(args):
    kwargs = {}
    for orig_key, val in zip(args[::2], args[1::2]):
        key = re.sub(r"^-{1,2}\b", "", orig_key)
        try:
            kwargs[key] = ast.literal_eval(val)
        except Exception as e:
            raise RuntimeError(f"Failed to parse the following argument: {orig_key} {val} See traceback above.") from e
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

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            raise exc_value

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

        for line in process.stdout:
            line_str = line.decode("utf-8").strip()
            print(line_str)

            if self.log:
                with open(os.path.join(logs_dir, "cascade_run.log"), "a") as log_file:
                    log_file.write(line_str + "\n")

        returncode = process.wait()
        if returncode:
            raise RunFailedException(
                f"Run of {script} failed. See traceback above."
                " The config and logs"
                f" will be kept at {self.run_dir}"
                " for post-mortem analysis"
            )


@click.command("run", context_settings={"ignore_unknown_options": True})
@click.argument("script", type=str)
@click.option("-y", is_flag=True, expose_value=True, help="Confirm run")
@click.option("--log", is_flag=True, default=False)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(script: str, y: bool, log: Optional[str], args: List[str]):
    """
    Run python scripts with the ability to override Config values and record logs
    """
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
