def test_load_obj_meta(any_line):
    meta0 = any_line.load_obj_meta(0)
    meta1 = any_line.load_obj_meta(1)

    assert meta0 != meta1
