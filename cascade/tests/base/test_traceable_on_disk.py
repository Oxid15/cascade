import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.base import MetaHandler, Traceable, TraceableOnDisk, default_meta_format


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_create(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.sync_meta()

    meta_path = os.path.join(tmp_path_str, "meta" + ext)

    assert os.path.exists(meta_path)
    assert trd.get_root() == os.path.dirname(meta_path)


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_recreate(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.sync_meta()

    meta = MetaHandler.read_dir(tmp_path_str)

    TraceableOnDisk(tmp_path_str, ext).sync_meta()

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert list(meta[0].keys()) == list(new_meta[0].keys())
    assert meta[0]["created_at"] == new_meta[0]["created_at"]
    assert meta[0]["updated_at"] != new_meta[0]["updated_at"]


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_recreate_comment(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.comment("Hello")

    meta = MetaHandler.read_dir(tmp_path_str)

    TraceableOnDisk(tmp_path_str, ext)

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert len(meta[0]["comments"]) == len(new_meta[0]["comments"])


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_update_comment(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.sync_meta()
    trd.comment("Hello")

    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.sync_meta()
    trd.comment("World")

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert len(new_meta[0]["comments"]) == 2


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_recreate_description(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.describe("Hello")

    meta = MetaHandler.read_dir(tmp_path_str)

    trd = TraceableOnDisk(tmp_path_str, ext)

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert meta[0]["description"] == new_meta[0]["description"]


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_on_disk_recreate_tags(tmp_path_str, ext):
    trd = TraceableOnDisk(tmp_path_str, ext)
    trd.tag(["hello", "world"])

    meta = MetaHandler.read_dir(tmp_path_str)

    trd = TraceableOnDisk(tmp_path_str, ext)

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert meta[0]["tags"] == new_meta[0]["tags"]


def test_on_disk_recreate_links(tmp_path_str):
    trd = TraceableOnDisk(tmp_path_str, ".json")
    tr = Traceable()
    trd.link(tr)

    meta = MetaHandler.read_dir(tmp_path_str)

    # Recreate empty and sync again
    trd = TraceableOnDisk(tmp_path_str, ".json")

    new_meta = MetaHandler.read_dir(tmp_path_str)

    assert meta[0]["links"] == new_meta[0]["links"]


def test_sync_idempotency(tmp_path_str):
    trd = TraceableOnDisk(tmp_path_str, ".json")
    tr = Traceable()

    trd.update_meta({"hello": "everyone"})
    trd.describe("description")
    trd.tag(["tags", "are", "cool"])
    trd.comment("Testing that nothing will duplicate after sync")
    trd.link(tr)

    # Sync two times
    trd.sync_meta()
    trd.sync_meta()

    meta = trd.get_meta()

    assert meta[0]["hello"] == "everyone"
    assert meta[0]["description"] == "description"
    assert set(meta[0]["tags"]) == {"tags", "are", "cool"}
    assert len(meta[0]["comments"]) == 1
    assert len(meta[0]["links"]) == 1


def test_default_meta_fmt(tmp_path_str):
    TraceableOnDisk(tmp_path_str, meta_fmt=None).sync_meta()
    assert os.path.join(tmp_path_str, "meta" + default_meta_format)


def test_infer_meta_fmt(tmp_path_str):
    TraceableOnDisk(tmp_path_str, meta_fmt=".yml").sync_meta()
    TraceableOnDisk(tmp_path_str, None).sync_meta()
    assert os.path.join(tmp_path_str, "meta.yml")


def test_infer_meta_fmt_conflict(tmp_path_str):
    TraceableOnDisk(tmp_path_str, meta_fmt=".yml").sync_meta()

    with pytest.warns(UserWarning):
        TraceableOnDisk(tmp_path_str, meta_fmt=".json").sync_meta()

    assert os.path.join(tmp_path_str, "meta.yml")
