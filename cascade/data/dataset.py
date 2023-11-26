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

from typing import Any, Generic, Iterable, Sequence, Sized, TypeVar, Union

from ..base import Meta, PipeMeta, Traceable, raise_not_implemented

T = TypeVar("T")


class Dataset(Generic[T], Traceable):
    """
    Base class of any module that constitutes a data-pipeline.
    In its basic idea is similar to torch.utils.data.Dataset.
    It does not define `__len__` for similar reasons.
    See `pytorch/torch/utils/data/sampler.py` note on this topic.

    See also
    --------
    cascade.base.Traceable
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __getitem__(self, index: Any) -> T:
        """
        Abstract method - should be defined in every successor
        """
        raise_not_implemented("cascade.data.Dataset", "__getitem__")

    def get_meta(self) -> PipeMeta:
        """
        Returns
        -------
        meta: PipeMeta
            A list where last element is this dataset's metadata.
            Meta can be anything that is worth to document about the dataset and its data.
            This is done in form of list to enable cascade-like calls in Modifiers and Samplers.
        """
        meta = super().get_meta()
        meta[0]["type"] = "dataset"
        return meta


class SizedDataset(Dataset[T], Sized):
    """
    An abstract class to represent a dataset
    with __len__ method present. Inheritance of
    this class should mean the presence of length.

    If your dataset does not have length defined, please
    use Dataset.

    See also
    --------
    cascade.data.Dataset
    """

    def __len__(self) -> int:
        raise_not_implemented("cascade.data.Dataset", "__len__")

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["len"] = len(self)
        return meta


class Iterator(Dataset):
    """
    Wraps Dataset around any Iterable. Does not have map-like interface.
    """

    def __init__(self, data: Iterable[T], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._data = data

    def __getitem__(self, item: Any) -> T:
        raise NotImplementedError(
            "Iterator explicitly forbids __getitem__ method."
            "Please, consider the use of Wrapper instead."
        )

    def __iter__(self) -> Iterable[T]:
        for item in self._data:
            yield item

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["obj_type"] = str(type(self._data))
        return meta


class BaseModifier(Dataset):
    def __init__(self, dataset: SizedDataset[T], *args: Any, **kwargs: Any) -> None:
        """
        Constructs a Modifier. Makes no transformations in initialization.

        Parameters
        ----------
        dataset: Dataset
            A dataset to modify
        """
        self._dataset = dataset
        super().__init__(*args, **kwargs)

    def get_meta(self) -> PipeMeta:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with `get_meta` of the last block.
        """
        self_meta = super().get_meta()
        self_meta += self._dataset.get_meta()
        return self_meta

    def from_meta(self, meta: Union[PipeMeta, Meta]) -> None:
        """
        Calls the same method as base class but does
        it cascade-like which allows to
        roll list of meta on a pipeline

        Parameters
        ----------
        meta : Union[PipeMeta, Meta]
            Meta of a single object or a pipeline
        """
        if isinstance(meta, list):
            super().from_meta(meta[0])
            if len(meta) > 1:
                self._dataset.from_meta(meta[1:])
        else:
            super().from_meta(meta)


class ItModifier(BaseModifier):
    """
    The Modifier for Iterator datasets

    See also
    --------
    cascade.data.Modifier
    """

    def __iter__(self) -> Iterable[T]:
        for item in self._dataset:
            yield item

    def get_meta(self) -> PipeMeta:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with `get_meta` of the last block.
        """
        self_meta = super().get_meta()
        self_meta += self._dataset.get_meta()
        return self_meta


class Wrapper(SizedDataset):
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

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["obj_type"] = str(type(self._data))
        return meta


class Modifier(BaseModifier):
    """
    Basic pipeline building block in Cascade. Every block which is not a data source should be
    a successor of Sampler or Modifier.
    This structure enables a workflow, when we have a data pipeline which consists of uniform blocks
    each of them has a reference to the previous one in its `_dataset` field. See get_meta method
    for example.
    Basically Modifier defines an arbitrary transformation on every dataset's item that is applied
    in a lazy manner on each `__getitem__` call.
    Applies no transformation if `__getitem__` is not overridden.
    """

    def __getitem__(self, index: Any) -> T:
        return self._dataset[index]

    def __iter__(self) -> Iterable[T]:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __len__(self) -> int:
        return len(self._dataset)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0]["len"] = len(self)
        return meta


class Sampler(Modifier):
    """
    Defines certain sampling over a Dataset. Its distinctive feature is that it changes the number
    of items in dataset. It can be used to build a batch sampler, random sampler, etc.

    See also
    --------
    cascade.data.CyclicSampler
    cascade.data.RandomSampler
    cascade.data.RangeSampler
    """

    def __init__(
        self, dataset: SizedDataset[T], num_samples: int, *args: Any, **kwargs: Any
    ) -> None:
        """
        Constructs a Sampler.

        Parameters
        ----------
            dataset: Dataset
                A dataset to sample from
            num_samples: int
                The number of samples
        """
        assert num_samples > 0, "The number of samples should be positive"
        super().__init__(dataset, *args, **kwargs)
        self._num_samples = num_samples

    def __len__(self) -> int:
        return self._num_samples
