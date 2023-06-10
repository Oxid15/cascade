import json
from flask import Flask, request
from ..data import Modifier
from ..base import JSONEncoder


class DatasetServer(Modifier):
    def __init__(self, dataset, **kwargs) -> None:
        super().__init__(dataset, **kwargs)
        self.app = Flask(__name__)

        @self.app.route("/")
        def get_meta():
            return self.get_meta()

        @self.app.route("/__getitem__", methods=["POST"])
        def get_item(*args, **kwargs):
            req = request.json
            data = self.__getitem__(req["idx"])
            data = self._serialize(data)
            return {"item": data}

        @self.app.route("/__len__", methods=["GET", "POST"])
        def ln():
            return {"len": self.__len__()}

    def _serialize(self, obj):
        return json.loads(JSONEncoder().encode(obj))

    def run(self, **kwargs):
        self.app.run(**kwargs)
