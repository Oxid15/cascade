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

import warnings
from abc import ABC, abstractmethod
from typing import (Any, Generic, Iterable, Iterator, Optional, Sequence,
                    Sized, TypeVar)

from ..base import Meta, Traceable
from .data_card import DataCard

T = TypeVar("T", covariant=True)


class BaseDataset(ABC, Generic[T], Traceable):
    """
    Base class of any object that constitutes a step in a data-pipeline

    See also
    --------
    cascade.base.Traceable
    """

    def __init__(self, *args: Any, data_card: Optional[DataCard] = None, **kwargs: Any) -> None:
        self._data_card = data_card
        super().__init__(*args, **kwargs)

    def get_meta(self) -> Meta:
        """
        Returns
        -------
        meta: Meta
            A list where last element is this dataset's metadata.
            Meta can be anything that is worth to document about the dataset and its data.
            This is done in form of list to enable cascade-like calls in Modifiers and Samplers.
        """
        meta = super().get_meta()
        meta[0]["type"] = "dataset"
        if self._data_card is not None:
            meta[0]["data_card"] = self._data_card.to_dict()
        return meta


class IteratorDataset(BaseDataset[T], Iterable[T]):
    """
    An abstract class to represent a dataset as
    an iterable object
    """

    def __iter__(self) -> Iterator[T]:
        return super().__iter__()


class Dataset(BaseDataset[T], Sized):
    """
    An abstract class to represent a dataset
    with __len__ method present. Inheritance of
    this class should mean the presence of length.

    If your dataset does not have length defined
    you can use Iterator

    See also
    --------
    cascade.data.Iterator
    """

    @abstractmethod
    def __getitem__(self, index: Any) -> T: ...

    @abstractmethod
    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[T]:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["len"] = len(self)
        return meta


class IteratorWrapper(IteratorDataset[T]):
    """
    Wraps IteratorDataset around any Iterable. Does not have map-like interface.
    """

    def __init__(self, data: Iterable[T], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._data = data

    def __iter__(self) -> Iterator[T]:
        for item in self._data:
            yield item

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["obj_type"] = str(type(self._data))
        return meta


class Wrapper(Dataset):
    """
    Wraps Dataset around any list-like object.
    """

    def __init__(self, obj: Sequence[T], *args: Any, **kwargs: Any) -> None:
        self._data = obj
        super().__init__(*args, **kwargs)

    def __getitem__(self, index: Any) -> T:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["obj_type"] = str(type(self._data))
        return meta


class SizedDataset(Dataset):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn("SizedDataset is deprecated since 0.14.0."
                      " Consider using older version or migrate to"
                      " Dataset, which is sized by default now")
        super().__init__(*args, **kwargs)
