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

from typing import Any, Callable, Dict, List, NoReturn, Union

from tqdm import tqdm
from typing_extensions import deprecated

from ..data.dataset import BaseDataset, T
from ..data.modifier import Modifier


class DataValidationException(Exception):
    """
    Raised when data validation fails
    """


def prettify_items(items: List[int]) -> str:
    if len(items) < 20:
        return str(items)
    else:
        return f'{", ".join(map(str, items[:5]))} ... {", ".join(map(str, items[-5:]))}'


class Validator(Modifier[T]):
    """
    Base class for validators. Defines basic ``__init__`` structure
    """

    @deprecated("Whole cascade.meta.validation is deprecated since 0.14.0 and is planned to"
                " be removed in 0.15.0. Use cascade.data.SchemaDataset instead")
    def __init__(
        self,
        dataset: BaseDataset[T],
        func: Union[Callable[[T], bool], List[Callable[[T], bool]]],
        **kwargs: Any,
    ) -> None:
        super().__init__(dataset, **kwargs)
        if isinstance(func, Callable):
            self._func = [func]
        else:
            self._func = func


class AggregateValidator(Validator[T]):
    """
    This validator accepts an aggregate function
    that accepts a ``Dataset`` and returns ``True`` or ``False``

    Example
    -------
    >>> from cascade.data import Wrapper
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> ds = AggregateValidator(ds, lambda x: len(x) == 5)
    """

    def __init__(
        self, dataset: BaseDataset[T], func: Callable[[BaseDataset[T]], bool], **kwargs
    ) -> None:
        super().__init__(dataset, func, **kwargs)

        bad_results = []
        for i, func in enumerate(self._func):
            if not func(self._dataset):
                bad_results.append(i)

        if len(bad_results):
            raise DataValidationException(f"Checks in positions {bad_results} failed")
        else:
            print("OK!")


class PredicateValidator(Validator[T]):
    """
    This validator accepts function that is applied to each item in a dataset
    and returns ``True`` or ``False``. Calls ``__getitem__``s of all previous
    datasets in ``__init__``.

    Example
    -------
    >>> from cascade.data import Wrapper
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> ds = PredicateValidator(ds, lambda x: x < 6)
    """

    def __init__(
        self,
        dataset: BaseDataset[T],
        func: Union[Callable[[T], bool], List[Callable[[T], bool]]],
        **kwargs: Any,
    ) -> None:
        super().__init__(dataset, func, **kwargs)

        bad_items = {j: [] for j in range(len(self._func))}
        for i, item in tqdm(enumerate(self._dataset), desc="Checking", leave=False):
            for j, func in enumerate(self._func):
                if not func(item):
                    bad_items[j].append(i)

        bad_counts = [len(bad_items[i]) for i in range(len(self._func))]
        if any(bad_counts):
            self._raise(bad_items)
        else:
            print("OK!")

    def _raise(self, items: Dict[int, List[int]]) -> NoReturn:
        bad_counts = [len(items[i]) for i in range(len(self._func))]

        failed_checks = [i for i in range(len(bad_counts)) if bad_counts[i]]
        failed_items = "\n".join([f"{i}: {prettify_items(items[i])}" for i in items])
        raise DataValidationException(
            f"Checks in positions {failed_checks} failed\n"
            f"Items failed by check:\n"
            f"{failed_items}"
        )
