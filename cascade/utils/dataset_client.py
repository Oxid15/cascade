import requests
from typing import Any
from ..data import Dataset


class DatasetClient:
    """
    Client for DatasetServer

    See also
    --------
    cascade.utils.dataset_server.DatasetServer
    """

    def __init__(self, host: str, **kwargs) -> None:
        """
        Parameters
        ----------
        host : str
            URL of dataset server
        """
        super().__init__(**kwargs)
        self._host = host

    def __getattribute__(self, name: str):
        if name == "_build_method" or name == "_host":
            return object.__getattribute__(self, name)
        return self._build_method(name)

    def _build_method(self, name: str):
        def method(*args, **kwargs):
            res = requests.post(
                self._host, json={"attr": name, "args": args, "kwargs": kwargs}
            )
            print(res.text)
            data = res.json()
            return data["result"]

        return method
