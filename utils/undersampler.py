from ..data import Sampler
from numpy import unique, min, histogram
from tqdm import trange


class UnderSampler(Sampler):
    def __init__(self, dataset):
        super().__init__(dataset, None)

        labels = [int(self._dataset[i][1]) for i in trange(len(self._dataset))]
        ulabels = unique(labels)
        label_nums, _ = histogram(labels, bins=len(ulabels))
        rem_nums = min(label_nums)

        self.rem_indices = []
        for label in ulabels:
            k = 0
            for _ in range(rem_nums):
                while labels[k] != label:
                    k += 1
                self.rem_indices.append(k)
        print(f'Original length was {len(self._dataset)} and new is {len(self)}')


    def __getitem__(self, index):
        idx = self.rem_indices[index]
        return self._dataset[idx]
    
    def __len__(self):
        return len(self.rem_indices)
