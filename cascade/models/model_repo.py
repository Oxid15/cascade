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

# import itertools
from typing import Any, Dict, Generator, Iterable, Optional

from ..base import TraceableOnDisk
from ..repos import Repo


class ModelRepo(Repo, TraceableOnDisk):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...


# class ModelRepoConcatenator(Repo):
#     """
#     The class to concatenate different Repos.
#     For the ease of use please, don't use it directly.
#     Just do `repo = repo_1 + repo_2` to unify two or more repos.
#     """

#     def __init__(self, repos: Iterable[Repo], *args: Any, **kwargs: Any) -> None:
#         super().__init__(*args, **kwargs)
#         self._repos = repos

#     def __getitem__(self, key) -> ModelLine:
#         pair = key.split("_")
#         if len(pair) <= 2:
#             raise KeyError(
#                 f"Key {key} is not in required format \
#             `<repo_idx>_..._<line_name>`. \
#             Please, use the key in this format. For example `0_line_1`"
#             )
#         idx, line_name = pair[0], "_".join(pair[1:])
#         idx = int(idx)

#         return self._repos[idx][line_name]

#     def __len__(self) -> int:
#         return sum([len(repo) for repo in self._repos])

#     def __iter__(self) -> Generator[ModelLine, None, None]:
#         # this flattens the list of lines
#         for line in itertools.chain(*[[line for line in repo] for repo in self._repos]):
#             yield line

#     def __add__(self, repo: ModelRepo):
#         return ModelRepoConcatenator([self, repo])

#     def __repr__(self) -> str:
#         return f"ModelRepoConcatenator of {len(self._repos)} repos, {len(self)} lines total"

#     def reload(self) -> None:
#         for repo in self._repos:
#             repo.reload()
