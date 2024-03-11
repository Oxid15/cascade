from cascade.base import PipeMeta
from cascade.data import BaseDataset, Modifier
from pydantic import BaseModel
from typing import Any, Optional

from cascade.data.dataset import Dataset


class Item(BaseModel):
    item: Any
    label: int


class CompatItem(BaseModel):
    item: Any
    label: int


class IncompatItem(BaseModel):
    item: Any
    label: str


class ItemTarget(Item):
    target: str


class SchemaDataset(BaseDataset):
    in_schema: Optional[BaseModel] = None


class SchemaModifier(SchemaDataset, Modifier):
    def __getattribute__(self, __name: str) -> Any:
        if __name == "_dataset" and self.in_schema is not None:
            return ValidationWrapper(super().__getattribute__(__name), self.in_schema)
        return super().__getattribute__(__name)


class ValidationWrapper(Modifier):
    def __init__(self, dataset: BaseDataset, schema: BaseModel, *args: Any, **kwargs: Any) -> None:
        self.schema = schema
        super().__init__(dataset, *args, **kwargs)

    def __getitem__(self, index: Any):
        item = super().__getitem__(index)
        if isinstance(item, BaseModel) or isinstance(item, dict):
            self.schema.model_validate(item, from_attributes=True)
        else:
            raise RuntimeError()
        return item


class TestDataset(SchemaDataset):
    def __getitem__(self, idx) -> Item:
        item = Item(item=0, label=1)
        return item

    def __len__(self) -> int:
        return 0


class TestDataset2(SchemaDataset):
    def __getitem__(self, idx) -> CompatItem:
        item = CompatItem(item=0, label=1)
        return item

    def __len__(self) -> int:
        return 0


class TestDataset3(SchemaDataset):
    def __getitem__(self, idx):
        item = dict(item=0, label=1)
        return item

    def __len__(self) -> int:
        return 0


class TestModifier(SchemaModifier):
    in_schema = Item

    def __getitem__(self, idx) -> ItemTarget:
        ds = self._dataset
        point = ds[idx]
        point["target"] = "lol"
        return ItemTarget(**point)


ds = TestDataset3()
ds.update_meta({"a": 1})
ds.comment("???")
ds = TestModifier(ds)
ds.comment("How about this? Modifier")

print(ds[0])
print(ds.get_meta())
