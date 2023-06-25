"""
Copyright 2022-2023 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Dict, List, Union

from ..base import Meta, PipeMeta

default_keys = ["data", "dataset"]


def skeleton(
    meta: Union[PipeMeta, Meta], keys: Union[List[Any], None] = None
) -> List[List[Dict[Any, Any]]]:
    """
    Parameters
    ----------
    meta: Union[PipeMeta, Meta]
        Meta of the pipeline
    keys: List[Any], optional
        The set of keys in meta where to search for previous dataset's meta.
        For example Concatenator when get_meta() is called stores meta of its
        datasets in the field called 'data'.
        If nothing given uses the default set of keys. Use this parameter only if
        your custom modifiers have additional fields you need to cover in this.

    Returns
    -------
    skeleton: List[List[Dict[Any, Any]]]
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
        if "name" in meta:
            s = {"name": meta["name"]}
        else:
            raise KeyError("Name not in meta")

        for key in keys:
            if key in meta:
                prev = skeleton(meta["data"])
                s[key] = prev
        skel.append(s)
    return skel
