from . import T, Dataset, Sampler


class RangeSampler(Sampler):
    def __init__(self, dataset: Dataset, start=None, stop=None, step=1, *args, **kwargs) -> None:
        if start is not None and stop is None:
            stop = start
            start = 0
        
        self._indices = [i for i in range(start, stop, step)]
        super().__init__(dataset, len(self._indices), *args, **kwargs)

    def __getitem__(self, index) -> T:
        internal_index = self._indices[index]
        return super().__getitem__(internal_index)
