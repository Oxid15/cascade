import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-ml",
    version='0.7.0',
    author='Ilia Moiseev',
    author_email='ilia.moiseev.5@yandex.ru',
    license='Apache License 2.0',
    description="ML-Engineering library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oxid15/cascade",
    project_urls={
        "Documentation": "https://oxid15.github.io/cascade",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir={"cascade": "./cascade",
                 'cascade_utils': './cascade/utils'},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'tqdm',
        'numpy',
        'pandas',
        'deepdiff',
        'pendulum',
        'plotly',
        'flatten_json',
        'pyyaml'
    ]
)
