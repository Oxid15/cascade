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
import datetime
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))
from cascade.base import HistoryLogger, MetaHandler


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_repo(tmp_path, ext):
    tmp_path = str(tmp_path)
    tmp_path = os.path.join(tmp_path, 'history' + ext)
    hl = HistoryLogger(tmp_path)
    mh = MetaHandler()

    obj = {
        'a': 0,
        'b': datetime.datetime.now()
    }

    hl.log(obj)
    obj_from_file = mh.read(tmp_path)

    assert 'history' in obj_from_file
    assert 'type' in obj_from_file
    assert len(obj_from_file['history']) == 1
    assert obj_from_file['type'] == 'history'
    assert obj_from_file['history'][0]['a'] == 0

    obj['a'] = 1

    hl.log(obj)
    obj_from_file = mh.read(tmp_path)

    assert 'history' in obj_from_file
    assert 'type' in obj_from_file
    assert len(obj_from_file['history']) == 2
    assert obj_from_file['history'][1]['a'] == 1
