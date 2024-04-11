from typing import Any, Optional

from .dataset import Dataset
from .modifier import Modifier
from .validation import SchemaValidator


class SchemaDataset(Dataset):
    in_schema: Optional[Any] = None

    def get_meta(self):
        meta = super().get_meta()
        if self.in_schema:
            meta[0]["in_schema"] = self.in_schema.model_json_schema()
        return meta


class SchemaModifier(SchemaDataset, Modifier):
    def __getattribute__(self, __name: str) -> Any:
        if __name == "_dataset" and self.in_schema is not None:
            return ValidationWrapper(super().__getattribute__(__name), self.in_schema)
        return super().__getattribute__(__name)


class ValidationWrapper(Modifier):
    def __init__(
        self, dataset: Dataset, schema: Any, *args: Any, **kwargs: Any
    ) -> None:
        self.validator = SchemaValidator(schema)
        super().__init__(dataset, *args, **kwargs)

    def __getitem__(self, index: Any):
        item = super().__getitem__(index)
        self.validator(item)
        return item
