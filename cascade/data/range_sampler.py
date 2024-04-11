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

from typing import Any, Optional

from .dataset import Dataset, T
from .modifier import Sampler


class RangeSampler(Sampler[T]):
    """
    Implements an interface of standard range in a dataset.

    Example
    -------
    >>> from cascade.data import RangeSampler, Wrapper
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> # Define start, stop and step exactly as in range()
    >>> sampler = RangeSampler(ds, 1, 5, 2)
    >>> for item in sampler:
    ...     print(item)
    ...
    2
    4
    >>> ds = Wrapper([1, 2, 3, 4, 5])
    >>> sampler = RangeSampler(ds, 3)
    >>> for item in sampler:
    ...     print(item)
    ...
    1
    2
    3
    """

    def __init__(
        self,
        dataset: Dataset[T],
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: int = 1,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
            dataset: SizedDataset
                A dataset to sample from
            start: int
                Start index in range - included
            stop: int
                Stop index in range - excluded
            step: int, default is 1
                Step of range
        Raises
        ------
        ValueError: when no start or stop present or
        when parameters given produce empty dataset
        """

        # Check if can build range
        if start is None and stop is None:
            raise ValueError(
                f"Either start or stop must be present\
                Got start = {start}, stop = {stop}"
            )

        # Check if only stop was passed
        if start is not None and stop is None:
            stop = start
            start = 0

        self._indices = [i for i in range(start, stop, step)]

        if len(self._indices) == 0:
            raise ValueError(
                f"Given combination of start, stop and step"
                f"produced empty dataset. Got start = {start}, stop = {stop}, step = {step}"
            )

        super().__init__(dataset, len(self._indices), *args, **kwargs)

    def __getitem__(self, index: int) -> T:
        internal_index = self._indices[index]
        return super().__getitem__(internal_index)
