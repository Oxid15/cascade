import os
import pytest

from cascade.base import MetaHandler


@pytest.mark.parametrize(
    'ext', [
        '.json',
        '.yml',
        '.yaml'
    ]
)
def test_random_pipeline_meta(tmp_path, utils_dataset, ext):
    tmp_path = str(tmp_path)
    mh = MetaHandler()

    filename = os.path.join(tmp_path, 'meta' + ext)

    meta = utils_dataset.get_meta()
    mh.write(filename, meta)
