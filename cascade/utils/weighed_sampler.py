"""
Copyright 2022 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Dict, Union, Tuple

from itertools import cycle
import numpy as np
from tqdm import trange

from ..data import SizedDataset, Sampler
from ..base import Meta


class WeighedSampler(Sampler):
    """
    Samples each class certain amount of times.

    Important
    ---------
    Sampler orders the items in the dataset in such way that items with each label go in row.
    Consider shuffling the dataset after sampling if label order is important.

    Example
    -------
    >>> from cascade import utils as cdu, data as cdd
    >>> ds = cdd.Wrapper([('item1', 0), ('item2', 1)])
    >>> ds = cdu.WeighedSampler(ds, {0: 2, 1: 1})
    >>> assert [item for item in ds] == [('item1', 0), ('item1', 0), ('item2', 1)]

    See also
    --------
    cascade.utils.OverSampler
    cascade.utils.UnderSampler
    cascade.data.RandomSampler
    """
    def __init__(self, dataset: SizedDataset[Tuple[Any, Any]],
                 partitioning: Union[Dict[Any, int], None] = None) -> None:
        """
        Parameters
        ----------
            dataset: Dataset
                A dataset to sample
            partitioning: Dict[Any, int], optional
                A dictionary with labels as keys and the number of samples as values.
                If some label omitted, assumes that it should be sampled the same number
                of times it is actually appears in the dataset.
        """
        labels = np.asarray([dataset[i][1] for i in trange(len(dataset))])
        ulabels, counts = np.unique(labels, return_counts=True)

        if partitioning is None:
            partitioning = {}

        self._check_partitioning(ulabels, partitioning)
        self._partitioning = partitioning

        # If label is omitted in partitioning, add it with true count
        for ulabel, count in zip(ulabels, counts):
            if ulabel not in self._partitioning:
                self._partitioning[ulabel] = count

        self._indices = []
        for label in self._partitioning:
            count = 0
            for idx in cycle(np.where(labels == label)[0]):
                if count >= self._partitioning[label]:
                    break

                self._indices.append(idx)
                count += 1

        ln = len(self._indices)
        assert ln == sum(partitioning.values()), \
            'The length should be equal to the sum of partitions - something went wrong'
        print(f'Original length was {len(dataset)} and new is {ln}')
        super().__init__(dataset, ln)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        idx = self._indices[index]
        return self._dataset[idx]

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]['partitioning'] = self._partitioning
        return meta

    def _check_partitioning(self, ulabels, partitioning) -> None:
        '''
        Checks if all labels that were passed in partitioning
        are present in dataset's unique labels
        '''
        for label in partitioning:
            if label not in ulabels:
                raise ValueError(f'Label {label} was not found in dataset\'s labels: {ulabels}')
