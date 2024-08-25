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

from typing import Any

import pandera.io as paio
from pandera import DataFrameSchema
from pandera.errors import SchemaError

from ...meta import AggregateValidator, DataValidationException
from ..tables import TableDataset


class PaSchemaValidator(AggregateValidator):
    """
    pandera-based data validator for ``TableDataset``s.
    It accepts TableDataset and schema.
    For more details on schemas see pandera's documentation.
    """

    def __init__(
        self, dataset: TableDataset, schema: DataFrameSchema, *args: Any, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        dataset: TabelDataset
            Dataset to validate
        schema:
            Schema of the table in the format that is acceptable by pandera
            or path to the YAML file with schema.
            For more details on schemas see pandera's documentation.

        Raises
        ------
        DataValidationException
        """
        super().__init__(
            dataset, *args, func=lambda x: self._validate(x, schema), **kwargs
        )

    @staticmethod
    def _validate(ds: TableDataset, schema) -> bool:
        try:
            if type(schema) is str:
                schema = paio.from_yaml(schema)
            schema.validate(ds._table)
        except SchemaError as e:
            raise DataValidationException(e)
        else:
            return True
