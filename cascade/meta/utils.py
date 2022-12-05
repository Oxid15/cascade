from typing import Union, List, Dict, Any

from ..base import Meta


default_keys = ['data', 'dataset']


def skeleton(
    meta: Union[Meta, Dict[Any, Any]],
    keys: Union[List[str], None] = None
) -> List[List[Dict[str, str]]]:
    """
    Parameters
    ----------
    meta: Union[Meta, Dict[Any, Any]]
        Meta of the pipeline
    keys: List[str], optional
        The set of keys in meta where to search for previous dataset's meta.
        For example Concatenator when get_meta() is called stores meta of its
        datasets in the field called 'data'.
        If nothing given uses the default set of keys. Use this parameter only if
        your custom modifiers have additional fields you need to cover in this.

    Returns
    -------
    skeleton: List[List[Dict[str, str]]]
    """

    if keys is not None:
        keys += default_keys
    else:
        keys = default_keys

    skel = []
    # The pipeline is given - represent each one with a new list
    if isinstance(meta, list):
        for ds in meta:
            s = skeleton(ds)
            skel.append(s)
    # The dataset is given - add it to the list and search for any
    # additional info in it
    elif isinstance(meta, dict):
        if 'name' in meta:
            s = {'name': meta['name']}
        else:
            raise KeyError('Name not in meta')

        for key in keys:
            if key in meta:
                prev = skeleton(meta['data'])
                s[key] = prev
        skel.append(s)
    return skel
