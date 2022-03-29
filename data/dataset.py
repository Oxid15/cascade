from typing import Generic, Iterable, TypeVar
from uuid import uuid1

T = TypeVar('T')


class Dataset(Generic[T]):
    def __getitem__(self, index) -> T:
        raise NotImplementedError

    def get_meta(self) -> dict:
        return {str(uuid1()): repr(self)}


class Wrapper(Dataset):
    def __init__(self, obj) -> None:
        self._data = obj

    def __getitem__(self, index) -> T:
        return self._data[index]
    
    def __len__(self) -> int:
        return len(self._data)



class Modifier(Dataset):
    def __init__(self, dataset) -> None:
        self._dataset = dataset
        self._index = -1

    def __getitem__(self, index) -> T:
        return self._dataset[index]

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if self._index < len(self) - 1:
            self._index += 1
            return self[self._index]
        else:
            self._index = -1
            raise StopIteration()

    def __len__(self) -> int:
        return len(self._dataset)
    
    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp} of size: {len(self)}'

    def get_meta(self) -> dict:
        meta = super().get_meta()
        meta.update(self._dataset.get_meta())
        return meta


class Sampler(Modifier):
    def __init__(self, dataset, num_samples) -> None:
        super(Sampler, self).__init__(dataset)
        self._num_samples = num_samples

    def __len__(self) -> int:
        return self._num_samples

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp} num_samples: {self._num_samples}'
