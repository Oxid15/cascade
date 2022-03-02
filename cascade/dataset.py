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
