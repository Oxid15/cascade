from typing import Generic, TypeVar


T = TypeVar('T')


class Dataset(Generic[T]):
    def __getitem__(self, index) -> T:
        raise NotImplementedError

    def get_meta(self, *args, **kwargs) -> dict:
        raise NotImplementedError()


class Modifier(Dataset):
    def __init__(self, dataset):
        self._dataset = dataset
        self._index = -1

    def __getitem__(self, index):
        return self._dataset[index]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self) - 1:
            self._index += 1
            return self[self._index]
        else:
            raise StopIteration()

    def __len__(self):
        return len(self._dataset)


class Sampler(Modifier):
    def __init__(self, dataset, num_samples):
        super(Sampler, self).__init__(dataset)
        self.num_samples = num_samples

    def __len__(self):
        return self.num_samples
