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

import os
from typing import Any
from . import MetaIOError
from .meta_handler import MetaHandler
from ..version import __version__

from deepdiff import DeepDiff


class HistoryLogger:
    """
    An interface to log meta into history files

    Example
    -------
    from cascade.base import HistoryLogger
    from cascade.data import Wrapper
    hl = HistoryLogger("wrapper_history_log.yml")
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
            self._log = {"history": [], "cascade_version": __version__, "type": "history"}

    def _reconstruct_state(self, n: int):
        state = self._log["history"][0]
        if n == 0:
            return state
        else:
            for i in range(0, n):
                state = 
                

    def log(self, obj: Any) -> None:
        """
        Logs the state of the object

        Parameters
        ----------
        obj: Any
            Meta data of the object
        """
        if len(self._log["history"]) == 0:
            self._log["history"].append(obj)
        else:

            diff = DeepDiff()
            self._log["history"].append(obj)

        try:
            MetaHandler.write(self._log_file, self._log)
        except MetaIOError as e:
            raise MetaIOError(f"Failed to write log file: {self._log_file}") from e

    def __getitem__(self, key: int):
        pass
