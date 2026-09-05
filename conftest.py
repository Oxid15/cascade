from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.rest import SkipParser

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=[
        "cascade/docs/source/*.rst",
        "cascade/docs/source/**/*.rst",
    ],
).pytest()
