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

from typing import Any

import requests

from ..data import Dataset
from .serializer import Serializer


class DatasetClient(Dataset):
    """
    Client for DatasetServer.

    DatasetClient is an interface for a dataset
    that lies under the DatasetServer.

    For every field or method call the client sends
    its name and arguments to the server to get the
    result.

    One can call any method that exists on the underlying
    dataset from the client and if the results are serializable
    should be able to receive results.

    Example
    -------
    This is how server can look - we wrap `FeatureTable` into the `DatasetServer`.

    ```python
    >>> from cascade.utils.dataset_server import DatasetServer
    >>> from cascade.utils.tables import FeatureTable
    >>> from cascade.data import Wrapper
    >>> import numpy as np
    >>> import pandas as pd
    >>> ds = FeatureTable(pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["a", "b", "c"]))
    >>> ds = DatasetServer(ds)
    >>> ds.run()
    ```

    This is what needs to be done on the client side.

    ```python
    from cascade.utils.dataset_client import DatasetClient

    >>> ds = DatasetClient('http://localhost:5000')
    >>> ds.get_meta()
    ```

    This call will be done on the side of the server in `FeatureTable`,
    the result is pickled, sent, then unpickled and returned on the cliend side.

    You can access any methods on server using client as long as return values can be pickled.

    See also
    --------
    cascade.utils.dataset_server.DatasetServer
    """

    def __init__(self, host: str, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        host : str
            URL of dataset server
        """
        super().__init__(**kwargs)
        self._host = host

    def __getattribute__(self, name: str):
        ALLOWED_NAMES = ["_deserialize", "_build_attr", "_host", "__dict__"]

        if name in ALLOWED_NAMES:
            return object.__getattribute__(self, name)
        return self._build_attr(name)

    def _build_attr(self, name: str):
        def attr(*args, **kwargs):
            request = {"attr": name}
            if args:
                request["args"] = Serializer.serialize(args)
            if kwargs:
                request["kwargs"] = Serializer.serialize(kwargs)

            res = requests.post(self._host, json=request)

            try:
                data = res.json()
            except requests.exceptions.JSONDecodeError as e:
                raise RuntimeError(res.text) from e

            if res.ok:
                return Serializer.deserialize(data["result"])
            else:
                if res.status_code == 404:
                    raise AttributeError(data.get("error"))

        return attr

    def __getitem__(self, index: Any) -> Any:
        return self._build_attr("__getitem__")(index)
