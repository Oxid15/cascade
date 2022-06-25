import warnings
from typing import List, Dict


class Traceable:
    def __init__(self, *args, meta_prefix=None, **kwargs) -> None:
        if meta_prefix is None:
            meta_prefix = {}
        if isinstance(meta_prefix, str):
            from . import MetaHandler

            meta_prefix = MetaHandler().read(meta_prefix)
        self.meta_prefix = meta_prefix

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

    def update_meta(self, obj: Dict) -> None:
        """
        Updates meta_prefix, which is then updates dataset's meta when get_meta() is called
        """
        if hasattr(self, 'meta_prefix'):
            self.meta_prefix.update(obj)
        else:
            self._warn_no_prefix()

    def _warn_no_prefix(self):
        warnings.warn('Object doesn\'t have meta_prefix. This may mean super().__init__() wasn\'t called somewhere')
