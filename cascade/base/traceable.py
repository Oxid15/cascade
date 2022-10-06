import warnings
from typing import List, Dict, Union


class Traceable:
    """
    Base class for everything that has metadata in cascade.
    Handles the logic of getting and updating internal meta prefix.
    """
    def __init__(self, *args, meta_prefix:Union[Dict, str] = None, **kwargs) -> None:
        """
        Parameters
        ----------
        meta_prefix: Union[Dict, str], optional
            The dictionary that is used to update object's meta in `get_meta` call.
            Due to the call of update can overwrite default values.
            If str - prefix assumed to be path and loaded using MetaHandler.
        
        See also
        --------
        cascade.base.MetaHandler
        """
        if meta_prefix is None:
            meta_prefix = {}
        elif isinstance(meta_prefix, str):
            meta_prefix = self._read_meta_from_file(meta_prefix)
        self._meta_prefix = meta_prefix

    @staticmethod
    def _read_meta_from_file(path: str) -> Union[List[Dict], Dict]:
        from . import MetaHandler
        return MetaHandler().read(path)

    def get_meta(self) -> List[Dict]:
        """
        Returns
        -------
        meta: List[Dict]
            A list where last element is this object's metadata.
            Meta can be anything that is worth to document about
            the object and its properties.
            Meta is list to allow the formation of pipelines.
        """
        meta = {
            'name': repr(self)
        }
        if hasattr(self, '_meta_prefix'):
            meta.update(self._meta_prefix)
        else:
            self._warn_no_prefix()
        return [meta]

    def update_meta(self, obj: Union[Dict, str]) -> None:
        """
        Updates `_meta_prefix`, which then updates
        dataset's meta when `get_meta()` is called
        """
        if isinstance(obj, str):
            obj = self._read_meta_from_file(obj)

        if hasattr(self, '_meta_prefix'):
            self._meta_prefix.update(obj)
        else:
            self._warn_no_prefix()

    @staticmethod
    def _warn_no_prefix() -> None:
        warnings.warn(
            'Object doesn\'t have _meta_prefix. '
            'This may mean super().__init__() wasn\'t'
            'called somewhere'
        )
