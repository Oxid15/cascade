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

from typing import List, Dict
import pandas as pd
from dask import dataframe as dd

from ..meta import AggregateValidator, DataValidationException
from ..data import Dataset, Modifier, Iterator, SequentialCacher


class TableDataset(Dataset):
    def __init__(self, *args, t=None, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(t, pd.DataFrame):
            self._table = t
        elif isinstance(t, TableDataset):
            self._table = t._table
        elif t is None:
            self._table = pd.DataFrame()
        else:
            raise TypeError('Input table is not a pandas.DataFrame nor TableDataset')

    def __getitem__(self, index):
        return self._table.iloc[index]

    def __repr__(self):
        return f'{super().__repr__()}\n {repr(self._table)}'

    def __len__(self):
        return len(self._table)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
                'name': repr(self),
                'columns': str(self._table.columns),
                'size': len(self),
                'info': str(self._table.describe())
            })
        return meta

    def to_csv(self, path, **kwargs):
        self._table.to_csv(path, **kwargs)


class TableFilter(TableDataset, Modifier):
    def __init__(self, dataset, mask, *args, **kwargs):
        super().__init__(dataset, t=dataset._table, *args, **kwargs)
        init_len = len(dataset)

        self._table = self._table[mask]
        print(f'Length before filtering: {init_len}, length after: {len(self._table)}')


class CSVDataset(TableDataset):
    def __init__(self, csv_file_path, *args, **kwargs):
        t = pd.read_csv(csv_file_path, *args, **kwargs)
        super().__init__(t=t, **kwargs)


class PartedTableLoader(Dataset):
    def __init__(self, csv_file_path, *args, **kwargs):
        super().__init__(**kwargs)
        self._table = dd.read_csv(csv_file_path, *args, **kwargs)

    def __getitem__(self, index):
        return self._table.get_partition(index).compute()

    def __len__(self):
        return self._table.npartitions


class TableIterator(Iterator):
    def __init__(self, csv_file_path, *args, chunk_size=1000, **kwargs):
        self.chunk_size = chunk_size
        super().__init__(pd.read_csv(csv_file_path, iterator=True, *args, **kwargs))

    def __next__(self):
        return self._data.get_chunk(self.chunk_size)


class LargeCSVDataset(SequentialCacher):
    def __init__(self, csv_file_path, *args, **kwargs):
        dataset = PartedTableLoader(csv_file_path, *args, **kwargs)
        self.num_batches = dataset._table.npartitions
        self.bs = self.len // self.num_batches

        super().__init__(dataset, self.bs)
        self.len = len(dataset._table)

    def _load(self, index):
        del self.batch
        self.batch = TableDataset(self._dataset[index])

    def __len__(self):
        return self.len


class NullValidator(TableDataset, AggregateValidator):
    def __init__(self, dataset, *args, **kwargs) -> None:
        super().__init__(dataset, self.check_nulls, *args, t=dataset._table, **kwargs)

    def check_nulls(self, x):
        mask = x._table.isnull().values
        if ~(mask.any()):
            return True
        else:
            total = mask.sum()
            by_columns = mask.sum(axis=0)
            missing = pd.DataFrame(by_columns.reshape(1, len(by_columns)), columns=x._table.columns)
            raise DataValidationException(
                f'There were NaN-values in {repr(self._dataset)}\n'\
                f'Total count: {total}\n'\
                f'By columns:\n'\
                f'{missing}'
            )
