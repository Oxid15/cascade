"""
Copyright 2022 Ilia Moiseev

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
import json

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import MetaViewer


def test(tmp_path):
    tmp_path = str(tmp_path)
    os.mkdir(os.path.join(tmp_path, 'model'))

    with open(os.path.join(tmp_path, 'test.json'), 'w') as f:
        json.dump({'name': 'test0'}, f)

    with open(os.path.join(tmp_path, 'model', 'test.json'), 'w') as f:
        json.dump({'name': 'test1'}, f)

    mv = MetaViewer(tmp_path)

    assert(len(mv) == 2)
    assert('name' in mv[0])
    assert('name' in mv[1])
    assert(mv[0]['name'] == 'test0')
    assert(mv[1]['name'] == 'test1')
