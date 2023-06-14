import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-ml",
    version="0.11.1",
    author="Ilia Moiseev",
    author_email="ilia.moiseev.5@yandex.ru",
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
    package_dir={"cascade": "./cascade", "cascade_utils": "./cascade/utils"},
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
    ],
)
