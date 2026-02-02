from phdai.chemistry import simple_consumption


def test_simple_consumption():
    t, c = simple_consumption((0, 1.0), 1.0, k=0.5)
    # concentration should decrease and be non-negative
    assert c[0] == 1.0
    assert c[-1] <= c[0]
    assert c[-1] >= 0
