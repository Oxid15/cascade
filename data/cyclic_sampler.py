from . import Sampler, T


class CyclicSampler(Sampler):
    def __getitem__(self, index) -> T:
        internal_index = index % len(self._dataset)
        return self._dataset[internal_index]
