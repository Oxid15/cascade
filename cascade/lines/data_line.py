import os
from typing import Any, Type

import pendulum
from deepdiff import DeepDiff

from ..base import MetaHandler, MetaIOError, PipeMeta
from ..data.dataset import Dataset
from .disk_line import DiskLine


class DataLine(DiskLine):
    def __init__(
        self,
        root: str,
        ds_cls: Type[Any] = Dataset,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(root, item_cls=ds_cls, *args, **kwargs)

    def load(self, num: int) -> None:
        raise NotImplementedError()

    def save(self, ds: Dataset) -> None:
        meta = ds.get_meta()

        if len(self._item_names) == 0:
            idx = 0
        else:
            idx = int(max(self._item_names)) + 1

            prev_folder_name = self._item_name_by_num(idx - 1)
            prev_path = os.path.join(self._root, prev_folder_name)
            if os.path.exists(prev_path):
                try:
                    prev_meta = MetaHandler.read_dir(prev_path)
                except MetaIOError:
                    pass
                else:
                    diff = DeepDiff(meta, prev_meta)
                    if not diff:
                        return

        # Should check just in case
        while True:
            folder_name = self._item_name_by_num(idx)
            model_folder = os.path.join(self._root, folder_name)
            if os.path.exists(model_folder):
                idx += 1
                continue

            os.makedirs(model_folder)
            break

        full_path = os.path.join(self._root, folder_name)

        meta[0]["path"] = full_path
        meta[0]["saved_at"] = pendulum.now(tz="UTC")

        MetaHandler.write(os.path.join(full_path, "meta" + self._meta_fmt), meta)
        self._item_names.append(folder_name)
        self.sync_meta()

    def __getitem__(self, num: int) -> Any:
        raise NotImplementedError()

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update({"type": "data_line"})
        return meta
