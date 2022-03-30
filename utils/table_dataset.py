from uuid import uuid1
import pandas as pd
from dask import dataframe as dd
from numpy import ceil

from ..data import Dataset, SequentialCacher


class TableDataset(Dataset):
    def __init__(self, t):
        if isinstance(t, pd.DataFrame):
            self._table = t
        elif isinstance(t, TableDataset):
            self._table = t._table
        else:
            raise TypeError('Input table is not a pandas.DataFrame nor TableDataset')

    def __getitem__(self, index):
        return self._table.iloc[index]

    def __repr__(self):
        return f'{super().__repr__()} {repr(self._table)}'

    def __len__(self):
        return len(self._table)

    def get_meta(self) -> dict:
        key = str(uuid1())
        meta = {
            key: {
                'name': repr(self),
                'size': len(self),
                'info': repr(self._table.describe())
            }
        }
        return meta


class TableFilter(TableDataset):
    def __init__(self, dataset, mask):
        super().__init__(dataset)
        init_len = len(dataset)

        self._table = self._table[mask]
        print(f'Length before filtering: {init_len}, length after: {len(self._table)}')


class CSVDataset(TableDataset):
    def __init__(self, csv_file_path, **kwargs):
        t = pd.read_csv(csv_file_path, **kwargs)
        super().__init__(t)


class PartedTableLoader(Dataset):
    def __init__(self, csv_file_path, **kwargs):
        self._table = dd.read_csv(csv_file_path, **kwargs)

    def __getitem__(self, index):
        return self._table.get_partition(index).compute()
    
    def __len__(self):
        return self._table.npartitions
