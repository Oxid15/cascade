from typing import Generic, TypeVar


T = TypeVar('T')


class Dataset(Generic[T]):
    def __getitem__(self, index) -> T:
        raise NotImplementedError


class Modifier(Dataset):
    def __init__(self, dataset):
        self._dataset = dataset

    def __getitem__(self, index):
        return self._dataset[index]

    def __len__(self):
        return len(self._dataset)


class Sampler(Modifier):
    def __init__(self, dataset, num_samples):
        super(Sampler, self).__init__(dataset)
        self.num_samples = num_samples

    def __len__(self):
        return self.num_samples
