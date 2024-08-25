"""
Copyright 2022-2024 Ilia Moiseev

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

from typing import Any, Callable, List, Tuple, Union

import pandas as pd
from tqdm import tqdm
from typing_extensions import Literal

from ...base import Meta
from ...data.dataset import Dataset, IteratorWrapper, T
from ...data.modifier import Modifier
from ...meta.validator import AggregateValidator, DataValidationException


class TableDataset(Dataset[T]):
    """
    Wrapper for ``pd.DataFrame``s which allows to manage metadata and perform
    validation.
    """

    def __init__(
        self,
        *args: Any,
        t: Union[pd.DataFrame, "TableDataset", None] = None,
        **kwargs: Any,
    ) -> None:
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
            raise TypeError("Input table is not a pandas.DataFrame nor TableDataset")

    def __getitem__(self, index: int) -> pd.Series:
        """
        Returns a row from table by index
        """
        return self._table.iloc[index]

    def __repr__(self) -> str:
        return f"{super().__repr__()}\n {repr(self._table)}"

    def __len__(self) -> int:
        """
        Returns length of the table
        """
        return len(self._table)

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update(
            {
                "columns": list(self._table.columns),
                "info": self._table.describe().to_dict(),
            }
        )
        return meta

    def to_csv(self, path: str, **kwargs: Any) -> None:
        """
        Saves the table to .csv file. Any kwargs are sent to
        ``pd.DataFrame.to_csv``.
        """
        self._table.to_csv(path, **kwargs)


class TableFilter(TableDataset, Modifier):
    """
    Filter for table values
    """

    def __init__(
        self, dataset: TableDataset, mask: List[bool], *args: Any, **kwargs: Any
    ) -> None:
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
        print(f"Length before filtering: {init_len}, length after: {len(self._table)}")


class CSVDataset(TableDataset):
    """
    Wrapper for .csv files.
    """

    def __init__(self, csv_file_path: str, *args: Any, **kwargs: Any) -> None:
        """
        Passes all args and kwargs to ``pd.read_csv``

        Parameters
        ----------
        csv_file_path:
            path to the .csv file
        """
        self._path = csv_file_path
        t = pd.read_csv(self._path, *args, **kwargs)
        super().__init__(t=t, **kwargs)


class TableIterator(IteratorWrapper):
    """
    Iterates over the table from path by the chunks.
    """

    def __init__(
        self, csv_file_path: str, *args: Any, chunk_size: int = 1000, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        csv_file_path: str
            Path to the .csv file
        chunk_size: int, optional
            number of rows to return in one __next__
        """
        self.chunk_size = chunk_size
        super().__init__(pd.read_csv(csv_file_path, iterator=True, *args, **kwargs))

    def __next__(self):
        return self._data.get_chunk(self.chunk_size)


class NullValidator(TableDataset, AggregateValidator):
    """
    Checks that there are no null values in the table.
    """

    def __init__(self, dataset: TableDataset, *args: Any, **kwargs: Any) -> None:
        super().__init__(dataset, self._check_nulls, *args, t=dataset._table, **kwargs)

    def _check_nulls(self, x: TableDataset) -> Literal[True]:
        mask = x._table.isnull().values
        if ~(mask.any()):
            return True
        else:
            total = mask.sum()
            by_columns = mask.sum(axis=0)
            missing = pd.DataFrame(
                by_columns.reshape(1, len(by_columns)), columns=x._table.columns
            )
            raise DataValidationException(
                f"There were NaN-values in {repr(self._dataset)}\n"
                f"Total count: {total}\n"
                f"By columns:\n"
                f"{missing}"
            )


class FeatureTable(TableDataset):
    def __init__(
        self, table: Union[TableDataset, pd.DataFrame], *args: Any, **kwargs: Any
    ) -> None:
        """
        Table dataset which allows to easily define and compute features

        Example
        -------
        ```python
        >>> import pandas as pd
        >>> from cascade.utils.tables import FeatureTable
        >>> df = pd.read_csv(r'data\t.csv', index_col=0)
        >>> df
        id  count  name
        0   0      1   aaa
        1   1      5   bbb
        2   2      0   ccc
        >>> ft = FeatureTable(df)
        >>> ft.get_features()
        ['id', 'count', ' name']
        >>> ft.add_feature('square', lambda df: df['count'] * df['count'])
        >>> def counts(df):
        >>>     return df['count'] * 2, df['count'] * 3

        >>> ft.add_feature(('count_2', 'count_3'), counts)
        >>> ft.get_features()
        ['id', 'count', ' name', 'square', ('count_2', 'count_3')]
        >>> ft.get_table(['count', ('count_2', 'count_3')])
           count  count_2  count_3
        0      1        2        3
        1      5       10       15
        2      0        0        0

        ```

        Parameters
        ----------
        table: Union[TableDataset, pd.DataFrame]
            The table to wrap
        """
        super().__init__(t=table, *args, **kwargs)
        self._computed_features = dict()
        self._computed_features_args = dict()
        self._computed_features_kwargs = dict()
        self._features = list(self._table.columns)

    def _validate_features(self, features: List[Union[str, Tuple[str]]]):
        missing_features = []
        for feat in features:
            if feat not in self._computed_features and feat not in self._table.columns:
                missing_features.append(feat)

        if len(missing_features) > 0:
            raise ValueError(
                f"Features {missing_features} was not found in table or list of computed features"
            )

    def get_features(self) -> List[Union[str, Tuple[str]]]:
        """
        Returns the list of feature names with all computed
        features added before

        Returns
        -------
        List[str]
            List of feature names
        """
        return list(self._features) + list(self._computed_features.keys())

    def _compute_feature(self, feat: Union[str, Tuple[str]]) -> None:
        func = self._computed_features[feat]
        args = self._computed_features_args[feat]
        kwargs = self._computed_features_kwargs[feat]

        result = func(self._table, *args, **kwargs)

        if isinstance(feat, str):
            feat = (feat,)
            result = (result,)

        for name, res in zip(feat, result):
            self._table[name] = res
            self._features.append(name)

    def get_table(
        self,
        features: Union[str, List[Union[Tuple[str], str]], None] = None,
        dropna: bool = False,
    ) -> pd.DataFrame:
        if isinstance(features, str):
            features = [features]
        elif features is None:
            features = self.get_features()

        self._validate_features(features)

        flat_features = []
        for feat in tqdm(features, desc="Computing features"):
            if isinstance(feat, str):
                flat_features.append(feat)
                if feat in self._table.columns:
                    continue
            else:
                flat_features += [*feat]
                if all([f in self._table.columns for f in feat]):
                    continue

            if feat in self._computed_features:
                self._compute_feature(feat)

            if dropna:
                self._table = self._table.dropna(how="any", subset=feat)

        return self._table[flat_features]

    def add_feature(
        self,
        name: Union[str, Tuple[str]],
        func: Callable[[pd.DataFrame], Union[pd.Series, Tuple[str]]],
        *args: Any,
        **kwargs: Any,
    ) -> None:  # What if feature already exists?
        self._computed_features[name] = func
        self._computed_features_args[name] = args
        self._computed_features_kwargs[name] = kwargs

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["computed_columns"] = list(self._computed_features.keys())
        meta[0]["computed_functions"] = {
            key: str(self._computed_features[key]) for key in self._computed_features
        }
        meta[0]["computed_functions_args"] = {
            key: str(self._computed_features_args[key])
            for key in self._computed_features_args
        }
        meta[0]["computed_functions_kwargs"] = {
            key: str(self._computed_features_kwargs[key])
            for key in self._computed_features_kwargs
        }
        return meta


class PartedTableLoader(TableDataset):
    def __init__(self, *args: Any, t=None, **kwargs: Any) -> None:
        raise ImportError(
            "PartedTableLoader was removed since 0.12.0, consider using older version"
        )


class LargeCSVDataset(TableDataset):
    def __init__(self, *args: Any, t=None, **kwargs: Any) -> None:
        raise ImportError(
            "LargeCSVDataset was removed since 0.12.0, consider using older version"
        )
