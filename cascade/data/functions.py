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

from typing import Any, Callable, List, Union

from ..base import PipeMeta
from .dataset import Dataset


class FDataset(Dataset):
    def __init__(self, *args: Any, f: Union[Callable[[Any], Any], None] = None, **kwargs: Any) -> None:
        self.result = f(*args, **kwargs)
        self._f_name = f.__name__
        super().__init__(*args, **kwargs)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["f"] = self._f_name
        return meta


class FModifier(FDataset):
    def __init__(self, *args: Any, f: Union[Callable[[Any], Any], None] = None, **kwargs: Any) -> None:
        datasets: List[FDataset] = []
        converted_args = []
        for i in range(len(args)):
            if isinstance(args[i], FDataset):
                datasets.append(args[i])
                converted_args.append(args[i].result)
            else:
                converted_args.append(args[i])
        self._datasets = datasets
        super().__init__(*converted_args, f=f, **kwargs)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        if len(self._datasets) == 1:
            meta += self._datasets[0].get_meta()
        elif len(self._datasets) != 0:
            meta += [[ds.get_meta() for ds in self._datasets]]
        return meta


def dataset(f: Callable[..., Any]) -> Callable[..., FDataset]:
    def wrapper(*args: Any, **kwargs: Any) -> FDataset:
        return FDataset(*args, **kwargs, f=f)
    return wrapper


def modifier(f: Callable[..., Any]) -> Callable[..., FModifier]:
    def wrapper(*args: Any, **kwargs: Any) -> FModifier:
        return FModifier(*args, **kwargs, f=f)
    return wrapper
