from ..data import Sampler
import numpy as np
from tqdm import trange


class OverSampler(Sampler):
    def __init__(self, dataset):
        super().__init__(dataset, None)

        labels = [int(self._dataset[i][1]) for i in trange(len(self._dataset))]
        ulabels = np.unique(labels)
        label_nums, _ = np.histogram(labels, bins=len(ulabels))
        add_nums = np.max(label_nums) - label_nums

        self.add_indices = []
        for label_idx, label in enumerate(ulabels):
            k = 0
            for _ in range(add_nums[label_idx]):
                while labels[k] != label:
                    k += 1
                self.add_indices.append(k)
        print(f'Original length was {len(self._dataset)} and new is {len(self)}')


    def __getitem__(self, index):
        if index < len(self._dataset):
            return self._dataset[index]
        else:
            idx = self.add_indices[index - len(self._dataset)]
            return self._dataset[idx]
    
    def __len__(self):
        return len(self._dataset) + len(self.add_indices)
