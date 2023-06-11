import requests
import pickle
from typing import Any

from ..data import Dataset


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
            res = requests.post(
                self._host, json={"attr": name, "args": args, "kwargs": kwargs}
            )
            data = res.json()
            return self._deserialize(data["result"])

        return attr

    def _deserialize(self, obj: str):
        return pickle.loads(bytes.fromhex(obj))

    def __getitem__(self, index: Any) -> Any:
        return self._build_attr("__getitem__")(index)
