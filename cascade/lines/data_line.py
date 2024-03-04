from typing import Any, Dict, Literal, Type

from ..base import PipeMeta
from ..data.dataset import Dataset
from .disk_line import DiskLine


class DataLine(DiskLine):
    def __init__(
        self,
        root: str,
        ds_cls: Type[Any] = Dataset,
        *args: Any,
        meta_prefix: Dict[Any, Any] | str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            root, item_cls=ds_cls, *args, meta_prefix=meta_prefix, **kwargs
        )

    def reload(self) -> None:
        pass

    def load(self, num: int, only_meta: bool = False) -> None:
        pass

    def save(self, obj: Any, only_meta: bool = False) -> None:
        pass

    def load_obj_meta(self, pathspec: str) -> PipeMeta: ...

    def __getitem__(self, num: int) -> Any:
        pass

    def __repr__(self) -> str:
        return f"DataLine of {len(self)} versions of {self._item_cls}"

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({"type": "data_line"})
        return meta
