import pandera.io as paio
from pandera.errors import SchemaError
from ..meta import AggregateValidator, DataValidationException


class PaSchemaValidator(AggregateValidator):
    """
    pandera-based data validator for `TableDataset`s.
    It accepts TableDataset and schema.
    For more details on schemas see pandera's documentation.
    """
    def __init__(self, dataset, schema, *args, **kwargs) -> None:
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
        super().__init__(dataset, *args, func=lambda x: self._validate(x, schema), **kwargs)

    @staticmethod
    def _validate(ds, schema) -> bool:
        try:
            if type(schema) == str:
                schema = paio.from_yaml(schema)
            schema.validate(ds._table)
        except SchemaError as e:
            raise DataValidationException(e)
        else:
            return True
