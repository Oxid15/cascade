from . import Modifier, T
from numpy import ceil


class SequentialCacher(Modifier):
    def __init__(self, dataset, batch_size=2) -> None:
        super().__init__(dataset)
        self.bs = batch_size
        self.num_batches = int(ceil(len(self._dataset) / self.bs))
        self.index = -1
        self.batch = None

    def _load(self, index):
        del self.batch
        self.batch = []

        start = index * self.bs
        end = min(start + self.bs, len(self._dataset))
        
        for i in range(start, end):
            self.batch.append(self._dataset[i])
        
        self.index += 1

    def __getitem__(self, index) -> T:
        batch_index = index // self.bs
        in_batch_idx = index % self.bs

        if batch_index != self.index:
            self._load(batch_index)

        return self.batch[in_batch_idx]
