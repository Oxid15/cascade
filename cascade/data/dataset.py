"""
Copyright 2022 Ilia Moiseev
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

from typing import Dict, Generic, Iterable, List, TypeVar, Any, Sized, Sequence
from ..base import Traceable, Meta

T = TypeVar('T')


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

    def __getitem__(self, index: int) -> T:
        """
        Abstract method - should be defined in every successor
        """
        raise NotImplementedError()

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
        meta[0]['type'] = 'dataset'
        return meta

    def __repr__(self) -> str:
        """
        Returns
        -------
        repr: str
            Representation of a Dataset. This repr used as a name for get_meta() method
            by default gives the name of class from basic repr

        See also
        --------
        cascade.data.Dataset.get_meta()
        """
        # Removes adress part of basic object repr and leading < symbol
        return super().__repr__().split()[0][1:]


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
    def len(self) -> int:
        raise NotImplementedError()


class Iterator(Dataset):
    """
    Wraps Dataset around any Iterable. Does not have map-like interface.
    """
    def __init__(self, data: Iterable[T], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._data = data

    def __getitem__(self, item: int) -> T:
        raise NotImplementedError()

    def __iter__(self) -> Iterable[T]:
        for item in self._data:
            yield item

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]['obj_type'] = str(type(self._data))
        return meta


class Wrapper(SizedDataset):
    """
    Wraps Dataset around any list-like object.
    """
    def __init__(self, obj: Sequence[T], *args: Any, **kwargs: Any) -> None:
        self._data = obj
        super().__init__(*args, **kwargs)

    def __getitem__(self, index: int) -> T:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]['len'] = len(self)
        meta[0]['obj_type'] = str(type(self._data))
        return meta


class Modifier(SizedDataset):
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

    def __getitem__(self, index: int) -> T:
        return self._dataset[index]

    def __iter__(self) -> T:
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __len__(self) -> int:
        return len(self._dataset)

    def get_meta(self) -> Meta:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with `get_meta` of the last block.
        """
        self_meta = super().get_meta()
        self_meta[0]['len'] = len(self)
        self_meta += self._dataset.get_meta()
        return self_meta


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
    def __init__(self, dataset: SizedDataset[T], num_samples: int,
                 *args: Any, **kwargs: Any) -> None:
        """
        Constructs a Sampler.

        Parameters
        ----------
            dataset: Dataset
                A dataset to sample from
            num_samples: int
                The number of samples
        """
        assert num_samples > 0, 'The number of samples should be positive'
        super().__init__(dataset, *args, **kwargs)
        self._num_samples = num_samples

    def __len__(self) -> int:
        return self._num_samples
