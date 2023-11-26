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

from flask import Flask, request

from ..data import Dataset, Modifier, T
from .serializer import Serializer


class DatasetServer(Modifier):
    """
    Wraps any Dataset into Flask app that
    accepts calls to root route with name of
    the attribute and optional arguments if
    it is a function.

    Server receives the attribute name and tries
    to get it from the underlying dataset.
    If it is a function, then it calls it.
    If it is something else just gets it.
    The results is serialized using pickle and
    sent in hex encoding to the client.

    To access any methods from the wrapped
    object one needs to access them from DatasetClient.

    See also
    --------
    cascade.utils.dataset_client.DatasetClient
    """

    def __init__(self, dataset: Dataset[T], **kwargs: Any) -> None:
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

            try:
                attr = getattr(self._dataset, attr)
            except AttributeError as e:
                return {"error": str(e)}, 404

            if callable(attr):
                try:
                    result = attr(*args, **kwargs)
                except Exception as e:
                    return {"error": str(e)}, 500
                try:
                    result = Serializer.serialize(result)
                except Exception as e:
                    return {"error": str(e)}, 500
            else:
                try:
                    result = Serializer.serialize(attr)
                except Exception as e:
                    return {"error": str(e)}, 500

            return {"result": result}, 200

    def run(self, *args: Any, **kwargs: Any):
        """
        Runs the server, all args and kwargs passed to
        Flask app.run()
        """
        self.app.run(*args, **kwargs)
