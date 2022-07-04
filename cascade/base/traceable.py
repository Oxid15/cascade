import warnings
from typing import List, Dict, Union


class Traceable:
    def __init__(self, *args, meta_prefix=None, **kwargs) -> None:
        if meta_prefix is None:
            meta_prefix = {}
        elif isinstance(meta_prefix, str):
            meta_prefix = self._read_meta_from_file(meta_prefix)
        self.meta_prefix = meta_prefix

    def _read_meta_from_file(self, path: str) -> Union[List[Dict], Dict]:
            from . import MetaHandler
            return MetaHandler().read(path)

    def get_meta(self) -> List[Dict]:
        """
        Returns
        -------
        meta: List[Dict]
            A list where last element is this object's metadata.
            Meta can be anything that is worth to document about the object and its properties.
            This is done in form of list to enable cascade-like calls in Modifiers and Samplers.
        """
        meta = {
            'name': repr(self)
        }
        if hasattr(self, 'meta_prefix'):
            meta.update(self.meta_prefix)
        else:
            self._warn_no_prefix()
        return [meta]

    def update_meta(self, obj: Union[Dict, str]) -> None:
        """
        Updates meta_prefix, which is then updates dataset's meta when get_meta() is called
        """
        if isinstance(obj, str):
            obj = self._read_meta_from_file(obj)

        if hasattr(self, 'meta_prefix'):
            self.meta_prefix.update(obj)
        else:
            self._warn_no_prefix()

    def _warn_no_prefix(self):
        warnings.warn('Object doesn\'t have meta_prefix. This may mean super().__init__() wasn\'t called somewhere')
