"""
Copyright 2022-2023 Ilia Moiseev

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

from typing import List, Union, Any, Literal
import pandas as pd
from dask import dataframe as dd

from ..meta import AggregateValidator, DataValidationException
from ..data import Dataset, Modifier, Iterator, SequentialCacher
from ..base import PipeMeta


class TableDataset(Dataset):
    """
    Wrapper for `pd.DataFrame`s which allows to manage metadata and perform
    validation.
    """
    def __init__(self, *args: Any, t: Union[pd.DataFrame, None] = None, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        t: optional
            pd.DataFrame or TableDataset to be set as table
        """
        super().__init__(*args, **kwargs)
        if isinstance(t, pd.DataFrame):
            self._table = t
        elif isinstance(t, TableDataset):
            self._table = t._table
        elif t is None:
            self._table = pd.DataFrame()
        else:
            raise TypeError('Input table is not a pandas.DataFrame nor TableDataset')

    def __getitem__(self, index: int) -> pd.Series:
        """
        Returns a row from table by index
        """
        return self._table.iloc[index]

    def __repr__(self) -> str:
        return f'{super().__repr__()}\n {repr(self._table)}'

    def __len__(self) -> int:
        """
        Returns length of the table
        """
        return len(self._table)

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({
            'name': repr(self),
            'columns': list(self._table.columns),
            'len': len(self),
            'info': self._table.describe().to_dict()
        })
        return meta

    def to_csv(self, path: str, **kwargs: Any) -> None:
        """
        Saves the table to .csv file. Any kwargs are sent to
        `pd.DataFrame.to_csv`.
        """
        self._table.to_csv(path, **kwargs)


class TableFilter(TableDataset, Modifier):
    """
    Filter for table values
    """
    def __init__(self, dataset: TableDataset,
                 mask: List[bool], *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        dataset: TableDataset
            Dataset to be filtered.
        mask: Iterable[bool]
            Binary mask to select values from table.
        """
        super().__init__(dataset, t=dataset._table, *args, **kwargs)
        init_len = len(dataset)

        self._table = self._table[mask]
        print(f'Length before filtering: {init_len}, length after: {len(self._table)}')


class CSVDataset(TableDataset):
    """
    Wrapper for .csv files.
    """
    def __init__(self, csv_file_path: str, *args: Any, **kwargs: Any) -> None:
        """
        Passes all args and kwargs to `pd.read_csv`

        Parameters
        ----------
        csv_file_path:
            path to the .csv file
        """
        t = pd.read_csv(csv_file_path, *args, **kwargs)
        super().__init__(t=t, **kwargs)


class PartedTableLoader(Dataset):
    """
    Works like CSVDataset, but uses dask to load tables
    and returns partitions on `__getitem__`.

    See also
    --------
    cascade.utils.CSVDataset
    """
    def __init__(self, csv_file_path: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._table = dd.read_csv(csv_file_path, *args, **kwargs)

    def __getitem__(self, index: int):
        """
        Returns partition under the index.
        """
        return self._table.get_partition(index).compute()

    def __len__(self) -> int:
        """
        Returns the number of partitions.
        """
        return self._table.npartitions


class TableIterator(Iterator):
    """
    Iterates over the table from path by the chunks.
    """
    def __init__(self, csv_file_path: str, *args: Any,
                 chunk_size: int = 1000, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        csv_file_path: str
            Path to the .csv file
        chunk_size: int, optional
            number of rows to return in one __next__
        """
        self.chunk_size = chunk_size
        super().__init__(pd.read_csv(csv_file_path,
                         iterator=True, *args, **kwargs))

    def __next__(self):
        return self._data.get_chunk(self.chunk_size)


class LargeCSVDataset(SequentialCacher):
    """
    SequentialCacher over large .csv file.
    Loads table by partitions.
    """
    def __init__(self, csv_file_path: str, *args: Any, **kwargs: Any) -> None:
        dataset = PartedTableLoader(csv_file_path, *args, **kwargs)
        self._ln = len(dataset._table)
        self.num_batches = dataset._table.npartitions
        self.bs = self._ln // self.num_batches
        super().__init__(dataset, self.bs)

    def _load(self, index: int) -> None:
        self._batch = TableDataset(t=self._dataset[index])

    def __len__(self) -> int:
        return self._ln


class NullValidator(TableDataset, AggregateValidator):
    """
    Checks that there are no null values in the table.
    """
    def __init__(self, dataset: TableDataset, *args: Any, **kwargs: Any) -> None:
        super().__init__(dataset, self._check_nulls,
                         *args, t=dataset._table, **kwargs)

    def _check_nulls(self, x: TableDataset) -> Literal[True]:
        mask = x._table.isnull().values
        if ~(mask.any()):
            return True
        else:
            total = mask.sum()
            by_columns = mask.sum(axis=0)
            missing = pd.DataFrame(by_columns.reshape(1, len(by_columns)), columns=x._table.columns)
            raise DataValidationException(
                f'There were NaN-values in {repr(self._dataset)}\n'
                f'Total count: {total}\n'
                f'By columns:\n'
                f'{missing}'
            )
