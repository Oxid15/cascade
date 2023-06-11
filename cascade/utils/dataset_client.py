from typing import Any

import requests

from ..data import Dataset
from .serializer import Serializer


class DatasetClient(Dataset):
    """
    Client for DatasetServer

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
        ALLOWED_NAMES = ["_deserialize", "_build_attr", "_host"]

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
            data = res.json()
            return Serializer.deserialize(data["result"])

        return attr

    def __getitem__(self, index: Any) -> Any:
        return self._build_attr("__getitem__")(index)
