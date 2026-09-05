import os

import pytest
from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.rest import SkipParser


@pytest.fixture
def sybil_cwd(request, tmp_path):
    namespace = request.node.example.namespace
    cwd = namespace.setdefault("__sybil_cwd", tmp_path)
    previous_cwd = os.getcwd()
    os.chdir(cwd)
    try:
        yield cwd
    finally:
        os.chdir(previous_cwd)


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=[
        "*.rst",
        "*.py",
    ],
    fixtures=["sybil_cwd"],
).pytest()
