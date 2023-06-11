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

import glob
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

    assert os.path.exists(os.path.join(tmp_path, 'dummy_1'))
    assert os.path.exists(os.path.join(tmp_path, '00001'))
    assert 2 == len(repo)


def test_save_load(tmp_path, dummy_model):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    repo.add_line('0', DummyModel)
    repo['0'].save(dummy_model)

    repo = ModelRepo(tmp_path, lines=[
        dict(name='0', model_cls=DummyModel)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_overwrite(tmp_path, ext):
    tmp_path = str(tmp_path)
    # If no overwrite repo will have 4 models
    repo = ModelRepo(tmp_path, overwrite=True, meta_fmt=ext)
    repo.add_line('vgg16', DummyModel)
    repo.add_line('resnet', DummyModel)

    # should delete repo to release loggers and be able to remove folder
    del repo

    repo = ModelRepo(tmp_path, overwrite=True)
    repo.add_line('densenet', DummyModel)
    repo.add_line('efficientnet', DummyModel)
    assert 2 == len(repo)


# This test is skipped due to its specificity
# it was created to support old interface where
# class was the first argument
# this is not supported and not common for a long time now
@pytest.mark.skip
def test_add_line(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    with pytest.raises(AssertionError):
        repo.add_line(DummyModel, 'vgg16')  # wrong argument order


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_reusage(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path, meta_fmt=ext)
    repo.add_line('vgg16', DummyModel)

    model = DummyModel()
    repo['vgg16'].save(model)

    # some time...

    repo = ModelRepo(tmp_path, meta_fmt=ext)
    repo.add_line('vgg16', DummyModel)
    assert len(repo['vgg16']) == 1


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_reusage_init_alias(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path, meta_fmt=ext)

    repo.add_line('vgg16', DummyModel)

    model = DummyModel()
    repo['vgg16'].save(model)

    # some time...

    repo = ModelRepo(tmp_path,
                     lines=[dict(name='vgg16', model_cls=DummyModel)],
                     meta_fmt=ext)
    assert len(repo['vgg16']) == 1


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path, meta_fmt=ext)
    repo.add_line('00000', DummyModel)
    repo.add_line('00001', DummyModel)

    meta = repo.get_meta()
    assert meta[0]['len'] == 2

    repo = ModelRepo(tmp_path, meta_fmt=ext)
    repo.add_line('00002', DummyModel)

    meta = repo.get_meta()
    assert meta[0]['len'] == 3


def test_add(tmp_path):
    tmp_path = str(tmp_path)

    repo_1 = ModelRepo(os.path.join(tmp_path, 'repo_1'))
    repo_1.add_line('line_1', DummyModel)
    repo_1['line_1'].save(DummyModel())

    repo_2 = ModelRepo(os.path.join(tmp_path, 'repo_2'))
    repo_2.add_line('line_1', DummyModel)
    repo_2.add_line('line_2', DummyModel)
    # repo_2['line_2'].save(DummyModel())

    repo = repo_1 + repo_2

    assert len(repo) == 3

    repo = repo + repo_2

    assert len(repo) == 5

    line_names = [
        '0_0_line_1',
        '0_1_line_1',
        '0_1_line_2',
        '1_line_1',
        '1_line_2'
    ]

    line_lens = [
        1, 0, 0, 0, 0
    ]

    for name, length in zip(line_names, line_lens):
        line = repo[name]
        assert len(line) == length


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_missing_repo_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate missing meta
    meta_path = os.path.join(repo_path, 'meta' + ext)
    os.remove(meta_path)

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_missing_line_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate missing meta
    meta_path = os.path.join(repo_path, '0', 'meta' + ext)
    os.remove(meta_path)

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_missing_model_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate missing meta
    meta_path = os.path.join(repo_path, '0', '00000', 'meta' + ext)
    os.remove(meta_path)

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_failed_repo_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate failed meta
    meta_path = os.path.join(repo_path, 'meta' + ext)
    assert os.path.exists(meta_path)
    with open(meta_path, 'w') as f:
        f.write("\t{{{: 'sorry, i am broken'")

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_failed_line_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate failed meta
    meta_path = os.path.join(repo_path, '0', 'meta' + ext)
    assert os.path.exists(meta_path)
    with open(meta_path, 'w') as f:
        f.write("\t{{{: 'sorry, i am broken'")

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_failed_model_meta(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo_path = os.path.join(tmp_path, 'repo')
    repo = ModelRepo(repo_path, meta_fmt=ext)
    repo.add_line('0', DummyModel)

    model = DummyModel()

    repo['0'].save(model)

    # simulate failed meta
    meta_path = os.path.join(repo_path, '0', '00000', 'meta' + ext)
    assert os.path.exists(meta_path)
    with open(meta_path, 'w') as f:
        f.write("\t{{{: 'sorry, i am broken'")

    repo = ModelRepo(repo_path, lines=[
        dict(name='0', model_cls=DummyModel, meta_fmt=ext)])
    model = repo['0'][0]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_get_line_names(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path, meta_fmt=ext)
    repo.add_line('a')
    repo.add_line('b')

    assert repo.get_line_names() == ['a', 'b']


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_integer_indices(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path, meta_fmt=ext)
    first_line = repo.add_line('a')
    last_line = repo.add_line('b')

    assert first_line == repo[0]
    assert last_line == repo[-1]


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml'
    ]
)
def test_auto_line_name(tmp_path, ext):
    repo = ModelRepo(str(tmp_path), meta_fmt=ext)
    repo.add_line()
    repo.add_line('test')
    repo.add_line()
    repo.add_line()

    names = repo.get_line_names()

    assert names == ['00000', 'test', '00002', '00003']

    repo = ModelRepo(str(tmp_path), meta_fmt=ext)

    names = repo.get_line_names()

    assert names == ['00000', '00002', '00003', 'test']


def test_no_logging(tmp_path):
    tmp_path = str(tmp_path)
    ModelRepo(tmp_path, log_history=False)

    metas = glob.glob(os.path.join(tmp_path, 'history.*'))

    assert len(metas) == 0
