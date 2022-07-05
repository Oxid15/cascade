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
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))
from cascade.models import ModelRepo
from cascade.tests.conftest import DummyModel


def test_repo(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    repo.add_line('dummy_1', DummyModel)
    repo.add_line('00001', DummyModel)

    assert(os.path.exists(os.path.join(tmp_path, 'dummy_1')))
    assert(os.path.exists(os.path.join(tmp_path, '00001')))
    assert(2 == len(repo))


def test_overwrite(tmp_path):
    tmp_path = str(tmp_path)
    # If no overwrite repo will have 4 models
    repo = ModelRepo(tmp_path, overwrite=True)
    repo.add_line('vgg16', DummyModel)
    repo.add_line('resnet', DummyModel)

    # should delete repo to release loggers and be able to remove folder
    del repo

    repo = ModelRepo(tmp_path, overwrite=True)
    repo.add_line('densenet', DummyModel)
    repo.add_line('efficientnet', DummyModel)
    assert(2 == len(repo))


def test_add_line(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    with pytest.raises(AssertionError):
        repo.add_line(DummyModel, 'vgg16')  # wrong argument order


def test_reusage(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    repo.add_line('vgg16', DummyModel)

    model = DummyModel()
    repo['vgg16'].save(model)

    # some time...

    repo = ModelRepo(tmp_path)
    repo.add_line('vgg16', DummyModel)
    assert(len(repo['vgg16']) == 1)


def test_reusage_init_alias(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)

    repo.add_line('vgg16', DummyModel)

    model = DummyModel()
    repo['vgg16'].save(model)

    # some time...

    repo = ModelRepo(tmp_path,
                        lines=[dict(
                            name='vgg16',
                            cls=DummyModel
                        )])
    assert(len(repo['vgg16']) == 1)


def test_meta(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    repo.add_line('00000', DummyModel)
    repo.add_line('00001', DummyModel)

    meta = repo.get_meta()
    assert(meta[0]['len'] == 2)

    repo = ModelRepo(tmp_path)
    repo.add_line('00002', DummyModel)

    meta = repo.get_meta()
    assert(meta[0]['len'] == 3)
