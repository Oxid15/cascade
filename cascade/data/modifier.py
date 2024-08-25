from typing import Any, Iterator

from ..base import Meta
from .dataset import BaseDataset, Dataset, IteratorDataset, T


class BaseModifier(BaseDataset[T]):
    def __init__(self, dataset: BaseDataset[T], *args: Any, **kwargs: Any) -> None:
        """
        Constructs a Modifier. Modifier represents a step in a pipeline -
        some data transformation

        Parameters
        ----------
        dataset: BaseDataset[T]
            A dataset to modify
        """
        self._dataset = dataset
        super().__init__(*args, **kwargs)

    def get_meta(self) -> Meta:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with ``get_meta`` of the last block.
        """
        self_meta = super().get_meta()
        self_meta += self._dataset.get_meta()
        return self_meta

    def from_meta(self, meta: Meta) -> None:
        """
        Calls the same method as base class but does
        it cascade-like which allows to
        roll a list of meta on a pipeline

        Parameters
        ----------
        meta : Meta
            Meta of a single object or a pipeline
        """
        if isinstance(meta, list):
            super().from_meta(meta[0])
            if len(meta) > 1:
                self._dataset.from_meta(meta[1:])
        else:
            super().from_meta(meta)


class IteratorModifier(BaseModifier[T], IteratorDataset[T]):
    """
    The Modifier for Iterator datasets

    See also
    --------
    cascade.data.Modifier
    cascade.data.Iterator
    """

    def __init__(self, dataset: IteratorDataset[T], *args: Any, **kwargs: Any) -> None:
        super().__init__(dataset, *args, **kwargs)

    def __iter__(self) -> Iterator[T]:
        return self._dataset.__iter__()

    def get_meta(self) -> Meta:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with ``get_meta`` of the last block.
        """
        self_meta = super().get_meta()
        self_meta += self._dataset.get_meta()
        return self_meta


class Modifier(BaseModifier[T]):
    """
    Basic pipeline building block in Cascade. Every block which is not a data source should be
    a successor of Sampler or Modifier.

    This structure enables having a data pipeline which consists of uniform blocks
    each of them has a reference to the previous one in its ``_dataset`` field

    Basically Modifier defines an arbitrary transformation on every dataset's item that is applied
    in a lazy manner on each ``__getitem__`` call.

    Applies no transformation if ``__getitem__`` is not overridden

    Does not change the length of a dataset. See Sampler for this functionality
    """

    def __getitem__(self, index: Any) -> T:
        return self._dataset[index]

    def __len__(self) -> int:
        return len(self._dataset)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["len"] = len(self)
        return meta


class Sampler(Modifier[T]):
    """
    Defines certain sampling over a Dataset.

    Its distinctive feature is that it changes the number
    of items in dataset.

    Can be used to build a batch sampler, random sampler, etc.

    See also
    --------
    cascade.data.CyclicSampler
    cascade.data.RandomSampler
    cascade.data.RangeSampler
    """

    def __init__(
        self, dataset: Dataset[T], num_samples: int, *args: Any, **kwargs: Any
    ) -> None:
        """
        Constructs a Sampler.

        Parameters
        ----------
            dataset: Dataset
                A dataset to sample from
            num_samples: int
                The number of samples to use as a new length
        """
        assert num_samples > 0, "The number of samples should be positive"
        super().__init__(dataset, *args, **kwargs)
        self._num_samples = num_samples

    def __len__(self) -> int:
        return self._num_samples
