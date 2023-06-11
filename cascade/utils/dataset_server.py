from typing import Any

from flask import Flask, request

from ..data import Modifier
from .serializer import Serializer


class DatasetServer(Modifier):
    def __init__(self, dataset, **kwargs: Any) -> None:
        super().__init__(dataset, **kwargs)
        self.app = Flask(__name__)

        @self.app.route("/", methods=["POST"])
        def attr():
            req = request.json
            attr = req.get("attr")
            args = req.get("args", [])
            kwargs = req.get("kwargs", {})

            if args:
                args = Serializer.deserialize(args)

            if kwargs:
                kwargs = Serializer.deserialize(kwargs)

            attr = getattr(self._dataset, attr)

            if callable(attr):
                return {"result": Serializer.serialize(attr(*args, **kwargs))}
            else:
                return {"result": Serializer.serialize(attr)}

    def run(self, **kwargs):
        self.app.run(**kwargs)
