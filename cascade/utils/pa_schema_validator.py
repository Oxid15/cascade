


class PaSchemaValidator(AggregateValidator):
    def __init__(self, dataset, schema, **kwargs) -> None:
        super().__init__(dataset, func=lambda x: self._validate(x, schema), **kwargs)

    def _validate(self, ds, schema) -> bool:
        try:
            schema.validate(ds._table)
        except SchemaError as e:
            raise DataValidationException(e)
        else:
            return True