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

import os
import traceback
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional

import click
from typing_extensions import Literal

from .common import create_container


@dataclass
class RemoveResult:
    """
    OKAY - file was deleted without any problems

    MISS - the artifact folder was not found or empty

    FAIL - something went wrong when removing a file
    """

    status: Literal["OKAY", "MISS", "FAIL"]
    path: Optional[str] = None
    traceback: Optional[str] = None


def remove_files(paths: List[str]) -> List[RemoveResult]:
    results = []
    for path in paths:
        if not os.path.exists(path):
            results.append(RemoveResult("MISS"))

        try:
            os.remove(path)
        except Exception:
            tb = traceback.format_exc()
            results.append(RemoveResult("FAIL", traceback=tb, path=path))
        else:
            results.append(RemoveResult("OKAY"))
    return results


def find_model_artifacts(path) -> List[str]:
    return [
        os.path.join(path, "artifacts", res) for res in os.listdir(os.path.join(path, "artifacts"))
    ]


def find_line_artifacts(path) -> List[str]:
    line = create_container("model_line", path)
    line_results = []
    for name in line.get_model_names():
        results = find_model_artifacts(os.path.join(path, name))
        line_results.extend(results)
    return line_results


def find_repo_artifacts(path) -> List[str]:
    repo = create_container("repo", path)
    repo_results = []
    for name in repo.get_line_names():
        results = find_line_artifacts(os.path.join(path, name))
        repo_results.extend(results)
    return repo_results


def find_workspace_artifacts(path) -> List[str]:
    wp = create_container("workspace", path)
    wp_results = []
    for name in wp.get_repo_names():
        results = find_repo_artifacts(os.path.join(path, name))
        wp_results.extend(results)
    return wp_results


find_obj_artifacts = {
    "model": find_model_artifacts,
    "line": find_line_artifacts,
    "model_line": find_line_artifacts,
    "repo": find_repo_artifacts,
    "workspace": find_workspace_artifacts,
}


@click.group("artifact")
@click.pass_context
def artifact(ctx):
    """
    Manage artifacts
    """


@artifact.command("rm")
@click.option("-y", is_flag=True, expose_value=True, help="Confirm")
@click.pass_context
def artifact_rm(ctx, y):
    """
    Remove artifacts from the whole container recursively
    """

    if ctx.obj["type"] in find_obj_artifacts:
        paths = find_obj_artifacts[ctx.obj["type"]](ctx.obj["cwd"])
    else:
        raise NotImplementedError(f"Cannot remove artifacts from {ctx.obj['type']}")

    if not y:
        click.confirm(f"Will try to delete {len(paths)}. Confirm?", abort=True)

    remove_results = remove_files(paths)

    c = Counter(res.status for res in remove_results)

    click.echo(f"Found {c['OKAY'] + c['FAIL']} files inside")
    click.echo(f"Removed: {c['OKAY']}")
    click.echo(f"Missing files: {c['MISS']}")
    click.echo(f"Failed: {c['FAIL']}")

    if c["FAIL"] != 0:
        for res in remove_results:
            if res.status == "FAIL":
                click.echo(f"Failed to remove {res.path}")
                click.echo(res.traceback)
