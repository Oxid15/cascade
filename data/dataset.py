from typing import Generic, TypeVar
from uuid import uuid1

T = TypeVar('T')


class Dataset(Generic[T]):
    def __getitem__(self, index) -> T:
        raise NotImplementedError

    def get_meta(self) -> dict:
        return {str(uuid1()): self.__repr__()}


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

    def get_meta(self) -> dict:
        meta = super().get_meta()
        meta.update(self._dataset.get_meta())
        return meta


class Sampler(Modifier):
    def __init__(self, dataset, num_samples) -> None:
        super(Sampler, self).__init__(dataset)
        self.num_samples = num_samples

    def __len__(self) -> int:
        return self.num_samples
