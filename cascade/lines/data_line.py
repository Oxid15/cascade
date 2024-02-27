from typing import Any

from cascade.base import PipeMeta

from ..base import TraceableOnDisk
from .line import Line


class DataLine(TraceableOnDisk, Line):
    def reload(self) -> None:
        pass

    def load(self, num: int, only_meta: bool = False) -> None:
        pass

    def save(self, obj: Any, only_meta: bool = False) -> None:
        pass

    def get_meta(self) -> PipeMeta:
        return super().get_meta()
