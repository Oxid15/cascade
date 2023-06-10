import requests
from ..data import Dataset


class DatasetClient(Dataset):
    def __init__(self, host: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._host = host

    def __getitem__(self, idx):
        res = requests.post(f"{self._host}/__getitem__", json={"idx": idx})
        data = res.json()
        return data["item"]

    def __len__(self):
        res = requests.post(f"{self._host}/__len__")
        data = res.json()
        return data["len"]
