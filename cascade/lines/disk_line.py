import os
from typing import Any, List, Literal, Type, Union

from ..base import MetaFromFile, MetaHandler, PipeMeta, TraceableOnDisk
from ..version import __version__
from .line import Line


class DiskLine(TraceableOnDisk, Line):
    def __init__(
        self,
        root: str,
        item_cls: Type[Any],
        meta_fmt: Literal[".json", ".yml", ".yaml", None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        root = os.path.abspath(root)
        self._item_cls = item_cls
        self._item_names = []

        if os.path.exists(self._root):
            self._load_item_names()
        else:
            os.mkdir(self._root)

        super().__init__(root, meta_fmt, *args, **kwargs)
        self.sync_meta()

    def reload(self) -> None:
        # Here update slugs in ModelLine
        self._load_item_names()

    def _load_item_names(self):
        if not os.path.isdir(self._root):
            raise ValueError(f"folder should be directory, got `{self._root}`")

        self._item_names = sorted(
            [
                item_folder
                for item_folder in os.listdir(self._root)
                if os.path.isdir(os.path.join(self._root, item_folder))
            ]
        )

    def __getitem__(self, num: int) -> Any:
        """
        Loads the item using `load` method of a given class
        """
        model = self.load(num)
        return model

    def __len__(self) -> int:
        """
        Returns
        -------
        A number of items in line
        """
        return len(self._item_names)

    def load(self, num: int) -> Any:
        item = self._item_cls.load(os.path.join(self._root, self._item_names[num]))
        return item

    def _read_meta_by_name(self, name: str) -> MetaFromFile:
        meta = MetaHandler.read_dir(os.path.join(self._root, name))
        return meta

    def _model_name_by_num(self, num: int) -> str:
        return f"{num:0>5d}"

    def _find_name_by_slug(self, slug: str) -> Optional[str]:
        if slug in self._slug2name_cache:
            return self._slug2name_cache[slug]

        for name in self._model_names:
            filepath = os.path.join(self._root, name, "SLUG")
            if not os.path.exists(filepath):
                continue
            with open(filepath, "r") as f:
                slug_from_file = f.read()
                self._slug2name_cache[slug_from_file] = name
                if slug == slug_from_file:
                    return name

    def _parse_item_name(self, item: Union[str, int]) -> str:
        if isinstance(item, int):
            name = self._item_name_by_num(item)
        elif isinstance(item, str):
            name = self._find_name_by_slug(item)
        else:
            raise TypeError(f"The argument of type {type(item)} is not supported")

        if not name:
            raise FileNotFoundError(
                f"Failed to find the item {item} in the line at {self._root}"
            )
        return name

    def __repr__(self) -> str:
        return f"{self.__class__}({len(self)}) items of {self._item_cls}"

    def load_obj_meta(self, path_spec: Union[str, int]) -> MetaFromFile:
        """
        Loads metadata of a item from disk

        Parameters
        ----------
        path_spec : Union[str, int]
            can be a slug e.g. `fair_squid_of_bliss` or a number

        Returns
        -------
        MetaFromFile
            Model metadata

        Raises
        ------
        FileNotFoundError
            Raises if failed to find the item with slug specified
        RuntimeError
            If found more than one metadata files in the specified
            item folder
        """
        name = self._parse_item_name(item)
        return self._read_meta_by_name(name)

    def get_item_names(self) -> List[str]:
        """
        Returns names of folders items live in

        Returns
        -------
        List[str]
            Only names of folders without whole path
        """
        return self._item_names

    def _save_only_meta(self, item: Any) -> None:
        self.save(item, only_meta=True)

    def create_item(self, *args: Any, **kwargs: Any) -> Any:
        """
        Creates a item using the class given on
        creation, registers log callbacks for it
        and returns

        Returns
        -------
        Any
            Created and prepared item
        """
        item = self._item_cls(*args, **kwargs)
        item.add_log_callback(self._save_only_meta)
        return item

    def get_meta(self) -> PipeMeta:
        meta = super().get_meta()
        meta[0].update(
            {
                "root": self._root,
                "item_cls": repr(self._item_cls),
                "len": len(self),
                "cascade_version": __version__,
            }
        )
        return meta
