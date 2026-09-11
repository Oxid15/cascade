"""
Copyright 2022-2026 Ilia Moiseev

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

import doctest
import os
from doctest import ELLIPSIS

import pytest
from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.rest import SkipParser

NUMBER = doctest.register_optionflag("NUMBER")

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
        DocTestParser(optionflags=NUMBER | ELLIPSIS),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=[
        "*.rst",
        "*.py",
    ],
    fixtures=["sybil_cwd"],
).pytest()
