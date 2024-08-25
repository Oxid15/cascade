"""
Copyright 2022-2024 Ilia Moiseev

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

import json
import os
from typing import Any, Dict

import pendulum
from deepdiff import DeepDiff, Delta
from typing_extensions import deprecated

from ..version import __version__
from . import MetaIOError
from .meta_handler import CustomEncoder, MetaHandler


@deprecated("This is deprecated since 0.14.0 and will be removed in 0.15.0")
class HistoryHandler:
    """
    An interface to log meta into history files

    Example
    -------
    from cascade.base import HistoryHandler
    from cascade.data import Wrapper
    hl = HistoryHandler("wrapper_history_log.yml")
    ds = Wrapper([0, 1, 2])
    hl.log(ds.get_meta())
    """

    def __init__(self, filepath: str) -> None:
        """
        Parameters
        ----------
        filepath: str
            Path to the history log file
        """
        self._log_file = filepath

        if os.path.exists(self._log_file):
            try:
                self._log = MetaHandler.read(self._log_file)
                if not self._is_log_compatible(self._log):
                    raise RuntimeError(
                        f"Log {filepath} is incompatible with history handler"
                        f" in cascade {__version__}"
                    )

                if isinstance(self._log, list):
                    raise RuntimeError(
                        f"Failed to initialize history logger due to unexpected object"
                        f" format - log is the instance of list and not dict."
                        f" Check your {self._log_file} file"
                    )
                if "history" not in self._log:
                    raise RuntimeError(
                        f"Failed to initialize history logger due to unexpected object"
                        f' format - "history" key is missing.'
                        f" Check your {self._log_file} file"
                    )
            except MetaIOError as e:
                raise MetaIOError(f"Failed to read log file: {self._log_file }") from e
        else:
            self._log = {
                "history": [],
                "cascade_version": __version__,
                "type": "history",
            }

    def _is_log_compatible(self, log: Dict[str, Any]) -> bool:
        if log.get("cascade_version"):
            return True
        return False

    def __len__(self) -> int:
        return len(self._log["history"]) + 1

    def log(self, obj: Any) -> None:
        """
        Logs the state of the object
        only if there is the change compared
        to the latest object state

        Parameters
        ----------
        obj: Any
            Meta data of the object

        Raises
        ------
        MetaIOError - if log writing fails
        """

        # Use serialize nac back to prevent false diffs due to
        # comparisons with meta from disk
        obj = CustomEncoder().obj_to_dict(obj)

        if not self._log.get("latest"):
            self._log["latest"] = obj
        else:
            diff = DeepDiff(obj, self._log["latest"])
            delta = Delta(
                diff, serializer=lambda x: json.dumps(x, cls=CustomEncoder)
            ).dumps()
            delta = json.loads(delta)

            # Log only if any change occured
            if delta:
                self._log["history"].append(
                    {
                        "id": len(self._log["history"]),
                        "time": pendulum.now(tz="UTC"),
                        "delta": delta,
                    }
                )
                self._log["latest"] = obj

        try:
            MetaHandler.write(self._log_file, self._log)
        except MetaIOError as e:
            raise MetaIOError(f"Failed to write log file: {self._log_file}") from e

    def get(self, key: int):
        """
        Restore and return object's state by the index
        """
        length = len(self._log["history"])

        # Number of states = number of deltas + 1 latest state
        if key == length:
            return self._log["latest"]
        else:
            state = self._log["latest"]
            for i in range(length - 1, -1, -1):
                delta = self._log["history"][i]["delta"]
                state = state + Delta(delta)
            return state
