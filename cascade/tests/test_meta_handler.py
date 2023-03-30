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
import pendulum
import numpy as np
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test(tmp_path, ext):
    tmp_path = str(tmp_path)
    mh = MetaHandler()
    mh.write(os.path.join(tmp_path, 'meta' + ext), {
        'name': 'test_mh',
        'array': np.zeros(4),
        'none': None,
        'date': pendulum.now(tz='UTC')
    })

    obj = mh.read(os.path.join(tmp_path, 'meta' + ext))

    assert (obj['name'] == 'test_mh')
    assert (obj['array'] == [0, 0, 0, 0])
    assert (obj['none'] is None)


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_overwrite(tmp_path, ext):
    tmp_path = os.path.join(str(tmp_path), 'test_mh_ow' + ext)

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
    assert (obj['name'] == 'first')


@pytest.mark.parametrize(
    'ext', [
        '.txt',
        '.md'
    ]
)
def test_text(tmp_path, ext):
    tmp_path = str(os.path.join(tmp_path, 'meta' + ext))
    mh = MetaHandler()

    info = '#Meta\n\n\n this is object for testing text files'
    with open(tmp_path, 'w') as f:
        f.write(info)

    obj = mh.read(tmp_path)

    assert (obj[tmp_path] == info)


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml',
        '.txt',
        '.md'
    ]
)
def test_not_exist(ext):
    mh = MetaHandler()

    # The case of non-existing file
    with pytest.raises(IOError) as e:
        mh.read('this_file_does_not_exist' + ext)
    assert e.typename == 'FileNotFoundError'


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_read_fail(tmp_path, ext):
    tmp_path = str(tmp_path)
    mh = MetaHandler()

    # Simulate broken syntax in file
    filename = os.path.join(tmp_path, 'meta' + ext)
    with open(filename, 'w') as f:
        f.write('\t{\t :this file is broken')

    # Test that file path is in error message
    with pytest.raises(IOError) as e:
        mh.read(filename)
    assert filename in e.value.args[0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_empty_file(tmp_path, ext):
    tmp_path = str(tmp_path)
    mh = MetaHandler()

    # Simulate empty file
    filename = os.path.join(tmp_path, 'meta' + ext)
    with open(filename, 'w') as f:
        f.write('')

    # Test that file path is in error message
    with pytest.raises(IOError) as e:
        mh.read(filename)
    assert filename in e.value.args[0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_random_pipeline_meta(tmp_path, dataset, ext):
    tmp_path = str(tmp_path)
    mh = MetaHandler()

    filename = os.path.join(tmp_path, 'meta' + ext)

    meta = dataset.get_meta()
    mh.write(filename, meta)
