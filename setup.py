import os
import sys
import setuptools

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.append(BASE_DIR)

import cascade


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-oxid15",
    version=cascade.__version__,
    author=cascade.__author__,
    author_email=cascade.__author_email__,
    description="Small ML-Engineering framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oxid15/cascade",
    project_urls={
        "Documentation": "https://oxid15.github.io/cascade",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)
