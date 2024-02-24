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

from typing import Any, NoReturn


class Server:
    def _raise_cannot_import_dash(self) -> NoReturn:
        raise ModuleNotFoundError(
            """
            Cannot import dash. It is conditional
            dependency you can install it
            using the instructions from https://dash.plotly.com/installation"""
        )

    def _raise_cannot_import_plotly(self) -> NoReturn:
        raise ModuleNotFoundError(
            """
            Cannot import plotly. It is conditional
            dependency you can install it
            using the instructions from plotly official documentation"""
        )

    def serve(self, **kwargs: Any) -> None:
        raise NotImplementedError()
