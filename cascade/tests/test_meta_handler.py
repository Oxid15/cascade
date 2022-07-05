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
import pendulum
import numpy as np

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler


def test(tmp_path):
    tmp_path = str(tmp_path)
    mh = MetaHandler()
    mh.write(os.path.join(tmp_path, 'meta.json'), 
    {
        'name': 'test_mh',
        'array': np.zeros(4),
        'none': None,
        'date': pendulum.now(tz='UTC')
    })

    obj = mh.read(os.path.join(tmp_path, 'meta.json'))

    assert(obj['name'] == 'test_mh')
    assert(all(obj['array'] == np.zeros(4)))
    assert(obj['none'] is None)


def test_overwrite(tmp_path):
    tmp_path = os.path.join(str(tmp_path), 'test_mh_ow.json')

    mh = MetaHandler()
    mh.write(
        tmp_path, 
        {'name': 'first'},
        overwrite=False)
    
    mh.write(
        tmp_path, 
        {'name': 'second'},
        overwrite=False)

    obj = mh.read(tmp_path)
    assert(obj['name'] == 'first')
