import requests
from typing import Any
from ..data import Dataset


class DatasetClient(Dataset):
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

    def __getitem__(self, idx: Any):
        res = requests.post("/".join((self._host, "__getitem__")), json={"idx": idx})
        data = res.json()
        return data["item"]

    def __len__(self):
        res = requests.get("/".join((self._host, "__len__")))
        data = res.json()
        return data["len"]
