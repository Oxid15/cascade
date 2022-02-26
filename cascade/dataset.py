from typing import Generic, TypeVar


T = TypeVar('T')


class Dataset(Generic[T]):
    def __getitem__(self, index) -> T:
        raise NotImplementedError
