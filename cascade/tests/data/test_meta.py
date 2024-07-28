

def test_meta(dataset):
    meta = dataset.get_meta()
    assert isinstance(meta, list)
    assert len(meta) > 0
