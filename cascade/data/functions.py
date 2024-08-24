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

from functools import wraps
from typing import Any, Callable, List, Union

from ..base import Meta
from .dataset import BaseDataset
from .validation import validate_in


class FunctionDataset(BaseDataset):
    def __init__(
        self, *args: Any, f: Union[Callable[[Any], Any], None] = None, **kwargs: Any
    ) -> None:
        self.result = f(*args, **kwargs)
        self._f_name = f.__name__
        super().__init__(*args, **kwargs)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["f"] = self._f_name
        return meta


class FunctionModifier(FunctionDataset):
    def __init__(
        self, *args: Any, f: Union[Callable[[Any], Any], None] = None, **kwargs: Any
    ) -> None:
        datasets: List[FunctionDataset] = []
        converted_args = []
        for i in range(len(args)):
            if isinstance(args[i], FunctionDataset):
                datasets.append(args[i])
                converted_args.append(args[i].result)
            else:
                converted_args.append(args[i])
        self._datasets = datasets
        super().__init__(*converted_args, f=f, **kwargs)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        if len(self._datasets) == 1:
            meta += self._datasets[0].get_meta()
        elif len(self._datasets) != 0:
            meta += [[ds.get_meta() for ds in self._datasets]]
        return meta


def dataset(f: Callable[..., Any], do_validate_in: bool = True) -> Callable[..., FunctionDataset]:
    """
    Thin wrapper to turn any function into a Cascade's Dataset.
    Use this if the function is the data source

    Will return FunctionDataset object. To get results of the execution
    use ``dataset.result`` field

    Parameters
    ----------
    f : Callable[..., Any]
        Function that produces data

    Returns
    -------
    Callable[..., FunctionDataset]
        Call this to get a dataset
    """
    if do_validate_in:
        f = validate_in(f)

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> FunctionDataset:
        return FunctionDataset(*args, **kwargs, f=f)

    return wrapper


def modifier(f: Callable[..., Any], do_validate_in: bool = True) -> Callable[..., FunctionModifier]:
    """
    Thin wrapper to turn any function into Cascade's Modifier
    Pass the returning value of a function
    that was previosly wrapped dataset or modifier. Will replace any
    dataset with ``dataset.result`` automatically if the function
    argument is ``FunctionDataset``.

    Parameters
    ----------
    f : Callable[..., Any]
        Function that modifies data

    Returns
    -------
    Callable[..., FunctionModifier]
        Call this to get a modifier
    """
    if do_validate_in:
        f = validate_in(f)

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> FunctionModifier:
        return FunctionModifier(*args, **kwargs, f=f)

    return wrapper
