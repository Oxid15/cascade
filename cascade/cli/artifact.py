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


def remove_files(path: str) -> List[RemoveResult]:
    if not os.path.exists(path):
        return [RemoveResult("MISS")]

    files = os.listdir(path)
    if len(files) == 0:
        return [RemoveResult("MISS")]

    results = []
    for name in files:
        file_path = os.path.join(path, name)
        try:
            os.remove(file_path)
        except Exception:
            tb = traceback.format_exc()
            results.append(RemoveResult("FAIL", traceback=tb, path=file_path))
        else:
            results.append(RemoveResult("OKAY"))
    return results


def remove_model_artifacts(path) -> List[RemoveResult]:
    return remove_files(os.path.join(path, "artifacts"))


def remove_line_artifacts(path) -> List[List[RemoveResult]]:
    line = create_container("line", path)
    line_results = []
    for name in line.get_model_names():
        results = remove_model_artifacts(os.path.join(path, name))
        line_results.append(results)
    return line_results


def remove_repo_artifacts(path) -> List[List[List[RemoveResult]]]:
    repo = create_container("repo", path)
    repo_results = []
    for name in repo.get_line_names():
        results = remove_line_artifacts(os.path.join(path, name))
        repo_results.append(results)
    return repo_results


def remove_wp_artifacts(path) -> List[List[List[List[RemoveResult]]]]:
    wp = create_container("workspace", path)
    wp_results = []
    for name in wp.get_repo_names():
        results = remove_repo_artifacts(os.path.join(path, name))
        wp_results.append(results)
    return wp_results


@click.group("artifact")
@click.pass_context
def artifact(ctx):
    """
    Manage artifacts
    """


@artifact.command("rm")
@click.pass_context
def artifact_rm(ctx):
    """
    Remove artifacts from the whole container recursively
    """
    results_list = []
    flat_results = []
    if ctx.obj["type"] == "model":
        results = remove_model_artifacts(ctx.obj["cwd"])
        results_list.append(results)
        flat_results.extend(results)
    elif ctx.obj["type"] == "line":
        line_results = remove_line_artifacts(ctx.obj["cwd"])
        for results in line_results:
            results_list.append(results)
            flat_results.extend(results)
    elif ctx.obj["type"] == "repo":
        repo_results = remove_repo_artifacts(ctx.obj["cwd"])
        for line_results in repo_results:
            for results in line_results:
                results_list.append(results)
                flat_results.extend(results)
    elif ctx.obj["type"] == "workspace":
        wp_results = remove_wp_artifacts(ctx.obj["cwd"])
        for repo_results in wp_results:
            for line_results in repo_results:
                for results in line_results:
                    results_list.append(results)
                    flat_results.extend(results)
    else:
        raise NotImplementedError(f"Cannot remove artifact from {ctx.obj['type']}")

    c = Counter(res.status for res in flat_results)

    click.echo(f"Found {c['OKAY'] + c['FAIL']} files in {len(results_list)} models")
    click.echo(f"Removed: {c['OKAY']}")
    click.echo(f"Missing files: {c['MISS']}")
    click.echo(f"Failed: {c['FAIL']}")

    if c["FAIL"] != 0:
        for res in flat_results:
            if res.status == "FAIL":
                click.echo(f"Failed to remove {res.path}")
                click.echo(res.traceback)
