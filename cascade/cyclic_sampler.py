from . import Sampler


class CyclicSampler(Sampler):
    def __getitem__(self, index):
        internal_index = index % len(self._dataset)
        return self._dataset[internal_index]
