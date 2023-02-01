import os


def test_js():
    assert os.system("node tests/test_verbs.js") == 0
