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
import sys
# import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler
from cascade.meta import DataRegistrator, DataCard


def test(tmp_path):
    tmp_path = str(tmp_path)
    tmp_path = tmp_path + '.yml'

    card = DataCard(
        name='name'
    )

    dr = DataRegistrator(tmp_path)
    dr.register(card)

    meta = MetaHandler().read(tmp_path)

    assert 'history' in meta
    assert len(meta['history']) == 1
    assert 'name' in meta['history'][0]
    assert meta['history'][0]['name'] == 'name'
