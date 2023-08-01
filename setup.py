import os
import sys
import setuptools

sys.path.append(os.path.dirname(__file__))
from cascade.version import __version__, __author__, __author_email__

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
        "Documentation": "https://oxid15.github.io/cascade",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['cascade = cascade.cli.cli:cli']},
    package_dir={"cascade": "./cascade"},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "tqdm>=4.64.1",
        "numpy>=1.18.5",
        "pandas>=1.4.0",
        "deepdiff>=5.8.0",
        "pendulum>=2.1.2",
        "flatten_json>=0.1.13",
        "pyyaml>=5.4.1",
        "coolname>=2.0.0",
        "click>=8.0.0",
    ],
)
