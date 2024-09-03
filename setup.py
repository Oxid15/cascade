import os
import sys

import setuptools

sys.path.append(os.path.dirname(__file__))
from cascade.version import __author__, __author_email__, __version__

_extras_require = {
    "opencv": ["opencv-python"],
    "pandera": ["pandera[io]>=0.6.5,<1"],
    "pil": ["Pillow>=8.4.0,<11"],
    "pydantic": ["pydantic>=1.9.2,<3"],
    "sklearn": ["scikit-learn>=0.24.2,<2"],
    "torch": ["torch>=1.10.2,<3"],
    "view": ["dash<3", "plotly>=5.7.0", "dash-renderjson==0.0.1"]
}

extras_require = {
    **_extras_require,
    "all": list(set(x for y in _extras_require.values() for x in y)),
}

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-ml",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    license="Apache License 2.0",
    description="ML-Engineering library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oxid15/cascade",
    project_urls={
        "Documentation": "https://oxid15.github.io/cascade/en/latest/index.html",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['cascade = cascade.cli.cli:cli']},
    package_dir={"cascade": "./cascade"},
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "tqdm>=4.64.1",
        "numpy>=1.18.5",
        "pandas>=1.1.5",
        "deepdiff>=5.0.2,<9",
        "pendulum>=2.1.2",
        "flatten_json==0.1.13",
        "pyyaml>=5.4.1",
        "coolname>=2.0.0",
        "click>=8.0.0",
        "typing-extensions>=4.1.1,<5"
    ],
    extras_require=extras_require
)
