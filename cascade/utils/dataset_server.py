import json
from flask import Flask, request
import pickle
from ..data import Modifier
from ..base import JSONEncoder
from typing import Any


class DatasetServer(Modifier):
    def __init__(self, dataset, **kwargs) -> None:
        super().__init__(dataset, **kwargs)
        self.app = Flask(__name__)

        @self.app.route("/", methods=["POST"])
        def attr():
            req = request.json
            attr = req.get("attr")
            args = req.get("args", [])
            kwargs = req.get("kwargs", {})

            attr = getattr(self._dataset, attr)

            if callable(attr):
                return {"result": self._serialize(attr(*args, **kwargs))}
            else:
                return {"result": self._serialize(attr)}

    def _serialize(self, obj: Any) -> str:
        return pickle.dumps(obj).hex()

    def run(self, **kwargs):
        self.app.run(**kwargs)
